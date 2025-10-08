"""
对话模型
存储用户与AI教练的交互历史
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ai_metrics import AIRequestMetrics


class Conversation(Base):
    """对话模型"""

    __tablename__ = "conversations"

    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # 外键
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )

    # 对话元数据
    title: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="对话标题(自动生成或用户设置)"
    )

    # 对话内容
    messages: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="对话消息数组 [{role: 'user'|'assistant', content: str, timestamp: str}]"
    )

    # AI提供商信息
    ai_provider_used: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="使用的AI提供商(phi-3.5/gpt-4o/claude-3.5-sonnet等)"
    )

    # 对话统计
    message_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="消息总数"
    )
    total_tokens_used: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="总token使用量"
    )
    estimated_cost: Mapped[float | None] = mapped_column(
        nullable=True,
        comment="估算成本(美元)"
    )

    # 对话上下文
    context_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="对话上下文摘要(用于长对话压缩)"
    )
    intent_classification: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="对话意图分类(health_query/energy_coaching/meditation等)"
    )

    # 对话状态
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="是否为活跃对话"
    )
    is_archived: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否已归档"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后一条消息时间"
    )

    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations"
    )
    ai_metrics: Mapped[List["AIRequestMetrics"]] = relationship(
        "AIRequestMetrics",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"

    def add_message(self, role: str, content: str, metadata: dict = None) -> None:
        """添加消息到对话"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata

        if not isinstance(self.messages, list):
            self.messages = []

        self.messages.append(message)
        self.message_count = len(self.messages)
        self.last_message_at = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> list:
        """获取最近的消息"""
        if not isinstance(self.messages, list):
            return []
        return self.messages[-limit:]

    @property
    def latest_message(self) -> dict | None:
        """获取最新消息"""
        if not isinstance(self.messages, list) or not self.messages:
            return None
        return self.messages[-1]
