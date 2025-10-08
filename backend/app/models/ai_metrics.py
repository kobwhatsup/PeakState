"""
AI请求指标模型
用于追踪AI使用情况、成本和性能
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIRequestMetrics(Base):
    """
    AI请求指标表

    用途:
    1. 追踪每个AI请求的详细指标
    2. 成本分析和预算控制
    3. 性能监控和优化
    4. 用户满意度统计
    """

    __tablename__ = "ai_request_metrics"

    # ============ 主键和关联 ============
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )

    conversation_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="会话ID"
    )

    # ============ 请求信息 ============
    user_message = Column(Text, nullable=False, comment="用户消息内容")
    ai_response = Column(Text, nullable=True, comment="AI响应内容")

    # ============ 意图和复杂度 ============
    intent_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="意图类型: greeting/data_query/advice_request/etc"
    )

    intent_confidence = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="意图分类置信度(0-1)"
    )

    complexity_score = Column(
        Integer,
        nullable=False,
        index=True,
        comment="复杂度分数(1-10)"
    )

    complexity_base = Column(Integer, nullable=True, comment="基础复杂度")
    complexity_context = Column(Integer, nullable=True, comment="上下文调整")
    complexity_user_pattern = Column(Integer, nullable=True, comment="用户模式调整")
    complexity_depth = Column(Integer, nullable=True, comment="对话深度调整")
    complexity_technical = Column(Integer, nullable=True, comment="专业程度调整")

    # ============ 路由决策 ============
    provider_used = Column(
        String(50),
        nullable=False,
        index=True,
        comment="实际使用的AI提供商: openai_gpt5/claude_sonnet_4/local_phi/etc"
    )

    routing_reason = Column(
        String(200),
        nullable=True,
        comment="路由决策理由"
    )

    # ============ Token使用 ============
    prompt_tokens = Column(
        Integer,
        nullable=True,
        default=0,
        comment="提示词token数"
    )

    completion_tokens = Column(
        Integer,
        nullable=True,
        default=0,
        comment="补全token数"
    )

    total_tokens = Column(
        Integer,
        nullable=True,
        default=0,
        index=True,
        comment="总token数"
    )

    # ============ 成本信息 ============
    estimated_cost_usd = Column(
        Float,
        nullable=True,
        default=0.0,
        comment="预估成本(美元)"
    )

    actual_cost_usd = Column(
        Float,
        nullable=True,
        default=0.0,
        index=True,
        comment="实际成本(美元)"
    )

    provider_rate_per_1k_tokens = Column(
        Float,
        nullable=True,
        comment="提供商费率(每1K tokens, 美元)"
    )

    cost_optimization_applied = Column(
        Boolean,
        default=False,
        comment="是否应用了成本优化"
    )

    # ============ 性能指标 ============
    request_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="请求时间"
    )

    response_timestamp = Column(
        DateTime,
        nullable=True,
        comment="响应时间"
    )

    actual_latency_ms = Column(
        Float,
        nullable=True,
        default=0.0,
        comment="实际响应延迟(毫秒)"
    )

    estimated_latency_ms = Column(
        Float,
        nullable=True,
        default=0.0,
        comment="预估响应延迟(毫秒)"
    )

    # ============ 工具使用 ============
    tools_used = Column(
        Text,
        nullable=True,
        comment="使用的工具列表(JSON数组)"
    )

    tool_call_count = Column(
        Integer,
        default=0,
        comment="工具调用次数"
    )

    # ============ 用户反馈 ============
    user_satisfaction = Column(
        Integer,
        nullable=True,
        comment="用户满意度评分(1-5)"
    )

    user_feedback = Column(
        Text,
        nullable=True,
        comment="用户反馈文本"
    )

    # ============ 错误信息 ============
    error_occurred = Column(
        Boolean,
        default=False,
        comment="是否发生错误"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )

    # ============ 时间戳 ============
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="记录创建时间"
    )

    # ============ 关系 ============
    user = relationship("User", back_populates="ai_metrics")
    conversation = relationship("Conversation", back_populates="ai_metrics")

    # ============ 索引 ============
    __table_args__ = (
        Index("ix_ai_metrics_user_created", "user_id", "created_at"),
        Index("ix_ai_metrics_provider_created", "provider_used", "created_at"),
        Index("ix_ai_metrics_cost", "actual_cost_usd"),
        Index("ix_ai_metrics_complexity_provider", "complexity_score", "provider_used"),
    )

    def __repr__(self) -> str:
        return (
            f"<AIRequestMetrics("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"intent={self.intent_type}, "
            f"complexity={self.complexity_score}, "
            f"provider={self.provider_used}, "
            f"cost=${self.actual_cost_usd:.6f}"
            f")>"
        )

    @property
    def latency_seconds(self) -> Optional[float]:
        """响应延迟(秒)"""
        if self.actual_latency_ms is not None:
            return self.actual_latency_ms / 1000
        return None

    @property
    def cost_per_token(self) -> Optional[float]:
        """每token成本"""
        if self.actual_cost_usd and self.total_tokens and self.total_tokens > 0:
            return self.actual_cost_usd / self.total_tokens
        return None

    @property
    def is_expensive(self) -> bool:
        """是否为高成本请求 (>$0.01)"""
        return bool(self.actual_cost_usd and self.actual_cost_usd > 0.01)

    @property
    def is_slow(self) -> bool:
        """是否为慢响应 (>5秒)"""
        return bool(self.actual_latency_ms and self.actual_latency_ms > 5000)
