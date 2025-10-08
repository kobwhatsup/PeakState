"""
聊天相关的Pydantic模型
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# ============ 聊天消息相关 ============

class MessageBase(BaseModel):
    """消息基础模型"""
    role: str = Field(..., description="消息角色: user | assistant | system")
    content: str = Field(..., description="消息内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class ChatMessage(MessageBase):
    """聊天消息完整模型"""
    timestamp: datetime = Field(..., description="消息时间戳")

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    conversation_id: Optional[UUID] = Field(None, description="会话ID,不提供则创建新会话")
    include_history: bool = Field(True, description="是否包含历史上下文")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "我今天感觉很累,精力不足",
                "conversation_id": None,
                "include_history": True
            }
        }


class ChatResponse(BaseModel):
    """聊天响应"""
    conversation_id: UUID = Field(..., description="会话ID")
    message: str = Field(..., description="AI回复内容")
    ai_provider: str = Field(..., description="使用的AI提供商")
    complexity_score: int = Field(..., description="复杂度评分(1-10)")
    intent: str = Field(..., description="识别的意图类型")
    tokens_used: Optional[int] = Field(None, description="消耗的token数")
    response_time_ms: int = Field(..., description="响应时间(毫秒)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    from_cache: bool = Field(False, description="是否来自缓存")
    cache_layer: Optional[str] = Field(None, description="缓存层级: L1 | L2 | L3")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "我理解你今天感到疲惫。让我们一起分析一下可能的原因...",
                "ai_provider": "phi-3.5",
                "complexity_score": 4,
                "intent": "energy_management",
                "tokens_used": 150,
                "response_time_ms": 85,
                "timestamp": "2025-01-15T10:30:00Z",
                "from_cache": False,
                "cache_layer": None
            }
        }


# ============ 会话历史相关 ============

class ConversationHistory(BaseModel):
    """会话历史"""
    conversation_id: UUID
    messages: List[ChatMessage] = Field(default_factory=list)
    message_count: int = Field(0, description="消息总数")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """会话列表项"""
    conversation_id: UUID
    title: Optional[str] = Field(None, description="会话标题(根据首条消息生成)")
    last_message: Optional[str] = Field(None, description="最后一条消息预览")
    message_count: int = Field(0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    conversations: List[ConversationListItem]
    total: int
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "精力管理咨询",
                        "last_message": "明天早上7点我会再次联系你...",
                        "message_count": 15,
                        "created_at": "2025-01-15T09:00:00Z",
                        "updated_at": "2025-01-15T18:00:00Z"
                    }
                ],
                "total": 5,
                "page": 1,
                "page_size": 20
            }
        }


# ============ 主动对话相关 ============

class ProactiveBriefingRequest(BaseModel):
    """主动简报请求(用于Celery任务)"""
    user_id: UUID
    briefing_type: str = Field(..., description="简报类型: morning | evening")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "briefing_type": "morning"
            }
        }


class ProactiveBriefingResponse(BaseModel):
    """主动简报响应"""
    conversation_id: UUID
    briefing_type: str
    message: str
    ai_provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# ============ AI分析相关 ============

class IntentAnalysis(BaseModel):
    """意图分析结果"""
    primary_intent: str = Field(..., description="主要意图")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    requires_empathy: bool = Field(False, description="是否需要同理心")
    suggested_actions: List[str] = Field(default_factory=list, description="建议操作")

    class Config:
        json_schema_extra = {
            "example": {
                "primary_intent": "energy_management",
                "confidence": 0.92,
                "requires_empathy": True,
                "suggested_actions": ["analyze_sleep_data", "suggest_energy_boost"]
            }
        }


class RoutingDecisionResponse(BaseModel):
    """路由决策响应(调试用)"""
    provider: str
    complexity: int
    intent: IntentAnalysis
    estimated_cost: float
    estimated_latency_ms: int
    reasoning: str = Field(..., description="选择此provider的原因")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "phi-3.5",
                "complexity": 3,
                "intent": {
                    "primary_intent": "simple_query",
                    "confidence": 0.95,
                    "requires_empathy": False,
                    "suggested_actions": []
                },
                "estimated_cost": 0.0001,
                "estimated_latency_ms": 80,
                "reasoning": "低复杂度查询,使用本地模型提供快速响应"
            }
        }
