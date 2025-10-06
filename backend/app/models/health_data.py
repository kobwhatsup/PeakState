"""
健康数据模型
存储来自Apple Health、Google Fit等来源的健康数据
支持端到端加密
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Float, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class HealthDataType(str):
    """健康数据类型枚举"""
    # 睡眠数据
    SLEEP_DURATION = "sleep_duration"           # 睡眠时长(小时)
    SLEEP_QUALITY = "sleep_quality"             # 睡眠质量评分(1-100)
    SLEEP_DEEP = "sleep_deep"                   # 深睡时长(小时)
    SLEEP_REM = "sleep_rem"                     # REM睡眠时长(小时)
    SLEEP_LIGHT = "sleep_light"                 # 浅睡时长(小时)

    # 心率变异性
    HRV = "hrv"                                 # 心率变异性(ms)
    HRV_RMSSD = "hrv_rmssd"                    # HRV RMSSD值
    HRV_SDNN = "hrv_sdnn"                      # HRV SDNN值

    # 心率
    HEART_RATE = "heart_rate"                   # 心率(bpm)
    HEART_RATE_RESTING = "heart_rate_resting"   # 静息心率
    HEART_RATE_WALKING = "heart_rate_walking"   # 步行心率

    # 活动数据
    STEPS = "steps"                             # 步数
    DISTANCE = "distance"                       # 距离(km)
    ACTIVE_ENERGY = "active_energy"             # 活动能量(kcal)
    EXERCISE_MINUTES = "exercise_minutes"       # 运动时长(分钟)

    # 血氧
    BLOOD_OXYGEN = "blood_oxygen"               # 血氧饱和度(%)

    # 压力
    STRESS_LEVEL = "stress_level"               # 压力水平(1-100)

    # 呼吸
    RESPIRATORY_RATE = "respiratory_rate"       # 呼吸频率(次/分钟)

    # 体温
    BODY_TEMPERATURE = "body_temperature"       # 体温(℃)

    # 主观评估
    ENERGY_LEVEL = "energy_level"               # 能量水平(1-10)
    MOOD = "mood"                               # 心情(1-10)
    FOCUS = "focus"                             # 专注度(1-10)


class HealthDataSource(str):
    """数据来源"""
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    OURA_RING = "oura_ring"
    WHOOP = "whoop"
    MANUAL = "manual"                           # 手动输入
    CALCULATED = "calculated"                   # 系统计算


class HealthData(Base):
    """健康数据模型"""

    __tablename__ = "health_data"

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

    # 数据类型和来源
    data_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="数据类型"
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="数据来源"
    )

    # 数据值
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="数据值"
    )
    unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="单位(hours/bpm/steps等)"
    )

    # 加密数据(可选,用于存储原始JSON数据)
    encrypted_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="加密的原始数据(Fernet加密)"
    )

    # 元数据(metadata是SQLAlchemy保留字,改用extra_data)
    extra_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="额外元数据(JSON格式)"
    )

    # 数据采集时间
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="数据采集时间"
    )

    # 数据同步信息
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="数据同步时间"
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="外部系统ID(用于防止重复同步)"
    )

    # 数据质量
    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="数据质量评分(0-1)"
    )
    is_anomaly: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否为异常值"
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

    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="health_data"
    )

    # 索引
    __table_args__ = (
        Index('ix_health_data_user_type_recorded', 'user_id', 'data_type', 'recorded_at'),
        Index('ix_health_data_user_recorded', 'user_id', 'recorded_at'),
        Index('ix_health_data_external_id', 'external_id'),
    )

    def __repr__(self) -> str:
        return (
            f"<HealthData(id={self.id}, user_id={self.user_id}, "
            f"type={self.data_type}, value={self.value}, recorded_at={self.recorded_at})>"
        )

    @classmethod
    def create_sleep_data(
        cls,
        user_id: uuid.UUID,
        duration: float,
        quality: float = None,
        deep: float = None,
        rem: float = None,
        light: float = None,
        recorded_at: datetime = None,
        source: str = HealthDataSource.MANUAL
    ) -> list:
        """创建睡眠数据集合"""
        recorded_at = recorded_at or datetime.utcnow()
        data_list = []

        # 睡眠时长
        data_list.append(cls(
            user_id=user_id,
            data_type=HealthDataType.SLEEP_DURATION,
            value=duration,
            unit="hours",
            source=source,
            recorded_at=recorded_at
        ))

        # 睡眠质量
        if quality is not None:
            data_list.append(cls(
                user_id=user_id,
                data_type=HealthDataType.SLEEP_QUALITY,
                value=quality,
                unit="score",
                source=source,
                recorded_at=recorded_at
            ))

        # 深睡
        if deep is not None:
            data_list.append(cls(
                user_id=user_id,
                data_type=HealthDataType.SLEEP_DEEP,
                value=deep,
                unit="hours",
                source=source,
                recorded_at=recorded_at
            ))

        # REM睡眠
        if rem is not None:
            data_list.append(cls(
                user_id=user_id,
                data_type=HealthDataType.SLEEP_REM,
                value=rem,
                unit="hours",
                source=source,
                recorded_at=recorded_at
            ))

        # 浅睡
        if light is not None:
            data_list.append(cls(
                user_id=user_id,
                data_type=HealthDataType.SLEEP_LIGHT,
                value=light,
                unit="hours",
                source=source,
                recorded_at=recorded_at
            ))

        return data_list
