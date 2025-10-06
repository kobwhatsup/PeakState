"""
聊天API端点
处理用户与AI教练的对话交互
"""

import time
from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    ConversationListResponse,
    ConversationListItem,
)
from app.crud import conversation as conversation_crud
from app.ai.orchestrator import AIOrchestrator
from app.ai.prompts import build_system_prompt


router = APIRouter()


# ============ 依赖注入 ============

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# 初始化AI Orchestrator(单例)
ai_orchestrator = AIOrchestrator()


# ============ 聊天端点 ============

@router.post("/send", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatRequest,
    db: DatabaseSession,
    current_user: CurrentUser
) -> ChatResponse:
    """
    发送消息给AI教练

    Args:
        request: 聊天请求(包含消息内容、会话ID等)
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        AI回复响应

    Raises:
        HTTPException 403: 用户订阅已过期,无访问权限
        HTTPException 404: 会话不存在
        HTTPException 500: AI服务错误
    """
    start_time = time.time()

    # 检查用户访问权限(订阅或试用状态)
    if not current_user.has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew to continue using AI coach."
        )

    # 1. 获取或创建会话
    if request.conversation_id:
        # 验证会话存在且属于当前用户
        conversation = await conversation_crud.get_conversation_by_id(
            db, request.conversation_id, current_user.id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )
    else:
        # 创建新会话
        conversation = await conversation_crud.create_conversation(
            db=db,
            user_id=current_user.id,
            initial_message=request.message,
            coach_type=current_user.coach_selection
        )

    # 2. 添加用户消息到会话
    await conversation_crud.add_message_to_conversation(
        db=db,
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=request.message
    )

    # 3. 获取会话上下文(历史消息)
    conversation_history = []
    if request.include_history:
        conversation_history = await conversation_crud.get_conversation_context(
            db=db,
            conversation_id=conversation.id,
            user_id=current_user.id,
            max_messages=10  # 最多包含最近10条消息
        )

    # 4. 构建用户画像和健康数据(TODO: 从数据库获取真实数据)
    user_profile = {
        "age": 35,  # TODO: 从User表获取
        "gender": "未知",
        "occupation": "未知",
        "timezone": "Asia/Shanghai",
        "days_active": (current_user.created_at - current_user.created_at).days
    }

    health_data = {
        # TODO: 从HealthData表聚合最近7天数据
        "sleep_avg": 7.2,
        "hrv_avg": 55.0,
        "steps_avg": 8500,
        "stress_level": "中等"
    }

    # 5. 构建系统提示词
    system_prompt = build_system_prompt(
        coach_type=current_user.coach_selection,
        scenario="general",
        user_profile=user_profile,
        health_data=health_data
    )

    # 6. AI路由决策和生成回复
    try:
        routing_decision = await ai_orchestrator.route_request(
            user_message=request.message,
            conversation_history=conversation_history,
            user_profile=user_profile
        )

        # 调用选定的AI提供商生成回复
        ai_response = await ai_orchestrator.generate_response(
            provider=routing_decision.provider,
            system_prompt=system_prompt,
            user_message=request.message,
            conversation_history=conversation_history,
            max_tokens=2000,
            temperature=0.7
        )

    except Exception as e:
        # AI服务错误处理
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

    # 7. 保存AI回复到会话
    await conversation_crud.add_message_to_conversation(
        db=db,
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="assistant",
        content=ai_response.content,
        metadata={
            "provider": routing_decision.provider.value,
            "complexity": routing_decision.complexity,
            "intent": routing_decision.intent.intent.value,
            "tokens": ai_response.tokens_used
        }
    )

    # 8. 更新会话AI提供商信息
    await conversation_crud.update_conversation_ai_provider(
        db=db,
        conversation_id=conversation.id,
        ai_provider=routing_decision.provider.value,
        tokens_used=ai_response.tokens_used
    )

    # 计算响应时间
    response_time_ms = int((time.time() - start_time) * 1000)

    # 9. 返回响应
    return ChatResponse(
        conversation_id=conversation.id,
        message=ai_response.content,
        ai_provider=routing_decision.provider.value,
        complexity_score=routing_decision.complexity,
        intent=routing_decision.intent.intent.value,  # 访问IntentClassification.intent.value
        tokens_used=ai_response.tokens_used,
        response_time_ms=response_time_ms
    )


@router.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser
) -> ConversationHistory:
    """
    获取指定会话的完整历史记录

    Args:
        conversation_id: 会话ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        会话历史对象

    Raises:
        HTTPException 404: 会话不存在或无权限访问
    """
    conversation = await conversation_crud.get_conversation_by_id(
        db, conversation_id, current_user.id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # 转换消息格式
    from app.schemas.chat import ChatMessage
    messages = [
        ChatMessage(
            role=msg.get("role", ""),
            content=msg.get("content", ""),
            metadata=msg.get("metadata"),
            timestamp=msg.get("timestamp")
        )
        for msg in conversation.messages
    ]

    return ConversationHistory(
        conversation_id=conversation.id,
        messages=messages,
        message_count=conversation.message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    db: DatabaseSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> ConversationListResponse:
    """
    获取用户的所有会话列表(分页)

    Args:
        db: 数据库会话
        current_user: 当前用户
        page: 页码(从1开始)
        page_size: 每页数量(1-100)

    Returns:
        会话列表响应
    """
    skip = (page - 1) * page_size

    # 获取会话列表
    conversations = await conversation_crud.get_user_conversations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        order_by="updated_at"
    )

    # 获取总数
    total = await conversation_crud.count_user_conversations(
        db=db,
        user_id=current_user.id
    )

    # 构建会话列表项
    conversation_items: List[ConversationListItem] = []

    for conv in conversations:
        # 生成会话摘要
        summary = await conversation_crud.get_conversation_summary(
            db=db,
            conversation_id=conv.id,
            user_id=current_user.id
        )

        if summary:
            conversation_items.append(
                ConversationListItem(
                    conversation_id=summary["conversation_id"],
                    title=summary["title"],
                    last_message=summary["last_message"],
                    message_count=summary["message_count"],
                    created_at=summary["created_at"],
                    updated_at=summary["updated_at"]
                )
            )

    return ConversationListResponse(
        conversations=conversation_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/new", response_model=ConversationHistory, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    db: DatabaseSession,
    current_user: CurrentUser
) -> ConversationHistory:
    """
    创建新的空会话

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        新创建的会话对象
    """
    conversation = await conversation_crud.create_conversation(
        db=db,
        user_id=current_user.id,
        coach_type=current_user.coach_selection
    )

    return ConversationHistory(
        conversation_id=conversation.id,
        messages=[],
        message_count=0,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser
):
    """
    删除指定会话

    Args:
        conversation_id: 会话ID
        db: 数据库会话
        current_user: 当前用户

    Raises:
        HTTPException 404: 会话不存在或无权限删除
    """
    success = await conversation_crud.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found or already deleted"
        )

    return None


# ============ 调试端点(仅开发环境) ============

@router.post("/debug/routing", response_model=dict)
async def debug_routing_decision(
    request: ChatRequest,
    current_user: CurrentUser
) -> dict:
    """
    调试端点: 查看AI路由决策(不实际调用AI)

    Args:
        request: 聊天请求
        current_user: 当前用户

    Returns:
        路由决策详情
    """
    routing_decision = await ai_orchestrator.route_request(
        user_message=request.message,
        conversation_history=[],
        user_profile={}
    )

    return {
        "provider": routing_decision.provider.value,
        "complexity": routing_decision.complexity,
        "intent": {
            "primary_intent": routing_decision.intent.primary_intent,
            "confidence": routing_decision.intent.confidence,
            "requires_empathy": routing_decision.intent.requires_empathy
        },
        "estimated_cost": routing_decision.estimated_cost,
        "estimated_latency_ms": routing_decision.estimated_latency_ms,
        "reasoning": routing_decision.reasoning
    }
