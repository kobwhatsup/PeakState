"""
Conversation CRUD操作
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.user import User


# ============ 创建操作 ============

async def create_conversation(
    db: AsyncSession,
    user_id: UUID,
    initial_message: Optional[str] = None,
    coach_type: Optional[str] = None
) -> Conversation:
    """
    创建新会话

    Args:
        db: 数据库会话
        user_id: 用户ID
        initial_message: 初始消息(可选)
        coach_type: 教练类型(可选,用于会话标记)

    Returns:
        创建的会话对象
    """
    conversation = Conversation(
        user_id=user_id,
        messages=[],
        message_count=0
    )

    # 如果有初始消息,添加到会话
    if initial_message:
        conversation.add_message(
            role="user",
            content=initial_message,
            metadata={"coach_type": coach_type} if coach_type else None
        )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation


# ============ 读取操作 ============

async def get_conversation_by_id(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """
    根据ID获取会话(验证用户权限)

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        user_id: 用户ID

    Returns:
        会话对象或None
    """
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_user_conversations(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    order_by: str = "updated_at"
) -> List[Conversation]:
    """
    获取用户的所有会话列表

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过数量
        limit: 返回数量
        order_by: 排序字段(updated_at | created_at)

    Returns:
        会话列表
    """
    order_column = (
        desc(Conversation.updated_at)
        if order_by == "updated_at"
        else desc(Conversation.created_at)
    )

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(order_column)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_user_conversations(
    db: AsyncSession,
    user_id: UUID
) -> int:
    """
    统计用户会话总数

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        会话总数
    """
    result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user_id)
    )
    return result.scalar_one()


async def get_latest_conversation(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Conversation]:
    """
    获取用户最新的会话

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        最新会话或None
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


# ============ 更新操作 ============

async def add_message_to_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Conversation:
    """
    向会话添加消息

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        user_id: 用户ID
        role: 消息角色(user | assistant | system)
        content: 消息内容
        metadata: 消息元数据

    Returns:
        更新后的会话对象

    Raises:
        ValueError: 如果会话不存在或无权限
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id)

    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found or access denied")

    # 使用模型方法添加消息
    conversation.add_message(role=role, content=content, metadata=metadata)

    # 更新updated_at时间戳
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(conversation)

    return conversation


async def update_conversation_ai_provider(
    db: AsyncSession,
    conversation_id: UUID,
    ai_provider: str,
    tokens_used: Optional[int] = None
) -> Conversation:
    """
    更新会话的AI提供商信息

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        ai_provider: AI提供商名称
        tokens_used: 使用的token数

    Returns:
        更新后的会话对象
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")

    conversation.ai_provider_used = ai_provider

    if tokens_used is not None:
        if conversation.total_tokens_used:
            conversation.total_tokens_used += tokens_used
        else:
            conversation.total_tokens_used = tokens_used

    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(conversation)

    return conversation


# ============ 删除操作 ============

async def delete_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> bool:
    """
    删除会话

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        user_id: 用户ID

    Returns:
        是否成功删除
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id)

    if not conversation:
        return False

    await db.delete(conversation)
    await db.commit()

    return True


async def delete_old_conversations(
    db: AsyncSession,
    user_id: UUID,
    keep_recent: int = 50
) -> int:
    """
    删除旧会话,保留最近N条

    Args:
        db: 数据库会话
        user_id: 用户ID
        keep_recent: 保留最近的会话数量

    Returns:
        删除的会话数量
    """
    # 获取要保留的会话ID列表
    result = await db.execute(
        select(Conversation.id)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
        .limit(keep_recent)
    )
    keep_ids = [row[0] for row in result.all()]

    # 删除不在保留列表中的会话
    delete_result = await db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.id.notin_(keep_ids) if keep_ids else True
        )
    )
    conversations_to_delete = delete_result.scalars().all()

    deleted_count = 0
    for conversation in conversations_to_delete:
        await db.delete(conversation)
        deleted_count += 1

    if deleted_count > 0:
        await db.commit()

    return deleted_count


# ============ 辅助函数 ============

async def get_conversation_summary(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    获取会话摘要信息

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        user_id: 用户ID

    Returns:
        会话摘要字典或None
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id)

    if not conversation:
        return None

    # 生成标题(使用首条用户消息的前30个字符)
    title = None
    last_message = None

    if conversation.messages:
        # 找到第一条用户消息
        for msg in conversation.messages:
            if msg.get("role") == "user":
                title = msg.get("content", "")[:30] + "..." if len(msg.get("content", "")) > 30 else msg.get("content", "")
                break

        # 获取最后一条消息
        if conversation.messages:
            last_msg = conversation.messages[-1]
            last_message = last_msg.get("content", "")[:50] + "..." if len(last_msg.get("content", "")) > 50 else last_msg.get("content", "")

    return {
        "conversation_id": conversation.id,
        "title": title or "新对话",
        "last_message": last_message,
        "message_count": conversation.message_count,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "ai_provider_used": conversation.ai_provider_used,
        "total_tokens_used": conversation.total_tokens_used
    }


async def get_conversation_context(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    max_messages: int = 10
) -> List[Dict[str, Any]]:
    """
    获取会话上下文(最近N条消息)

    Args:
        db: 数据库会话
        conversation_id: 会话ID
        user_id: 用户ID
        max_messages: 返回最多消息数

    Returns:
        消息列表
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id)

    if not conversation or not conversation.messages:
        return []

    # 返回最近的N条消息
    return conversation.messages[-max_messages:] if len(conversation.messages) > max_messages else conversation.messages
