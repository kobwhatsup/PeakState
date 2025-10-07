"""
用户模型
包含认证、订阅、教练选择等核心字段
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.health_data import HealthData


class CoachType(str, Enum):
    """AI教练类型"""
    SAGE = "sage"          # 智者型 - 温和睿智,启发式引导
    COMPANION = "companion"  # 伙伴型 - 亲切自然,温暖陪伴
    EXPERT = "expert"      # 专家型 - 专业精准,数据驱动


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # 认证信息
    phone_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        comment="手机号(登录凭证)"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt加密密码"
    )

    # 用户配置
    coach_selection: Mapped[str] = mapped_column(
        SQLEnum("mentor", "coach", "doctor", "zen", "sage", "companion", "expert", name="coach_type", create_type=False),
        default="companion",
        server_default="companion",
        nullable=False,
        comment="AI教练类型选择"
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Asia/Shanghai",
        nullable=False,
        comment="用户时区"
    )

    # 订阅状态
    is_subscribed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已订阅"
    )
    subscription_start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="订阅开始时间"
    )
    subscription_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="订阅到期时间"
    )
    subscription_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="订阅类型(monthly/yearly)"
    )

    # 试用状态
    is_trial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否试用中"
    )
    trial_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="试用到期时间"
    )

    # 用户状态
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="账号是否激活"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="手机号是否验证"
    )

    # 用户偏好设置
    morning_briefing_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用早报"
    )
    morning_briefing_time: Mapped[str] = mapped_column(
        String(5),
        default="07:00",
        nullable=False,
        comment="早报推送时间"
    )
    evening_review_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用晚间复盘"
    )
    evening_review_time: Mapped[str] = mapped_column(
        String(5),
        default="22:00",
        nullable=False,
        comment="晚间复盘时间"
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
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )

    # 关系
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    health_data: Mapped[List["HealthData"]] = relationship(
        "HealthData",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload"  # 不自动加载，避免模型不一致问题
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone={self.phone_number}, subscribed={self.is_subscribed})>"

    @property
    def is_subscription_active(self) -> bool:
        """检查订阅是否有效"""
        if not self.is_subscribed:
            return False
        if self.subscription_end_date is None:
            return False
        return self.subscription_end_date > datetime.utcnow()

    @property
    def is_trial_active(self) -> bool:
        """检查试用是否有效"""
        if not self.is_trial:
            return False
        if self.trial_end_date is None:
            return False
        return self.trial_end_date > datetime.utcnow()

    @property
    def has_access(self) -> bool:
        """检查用户是否有访问权限(订阅或试用中)"""
        return self.is_subscription_active or self.is_trial_active
