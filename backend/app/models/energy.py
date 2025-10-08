"""
精力相关数据模型
包括精力预测、个性化基线、精力模式等
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Float, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class EnergyPrediction(Base):
    """精力预测记录"""

    __tablename__ = "energy_predictions"

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

    # 预测时间
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="预测生成时间"
    )
    target_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="预测目标时间"
    )

    # 预测结果
    energy_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="精力等级: high/medium/low"
    )
    energy_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="精力分数(1-10)"
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="预测置信度(0-1)"
    )

    # 影响因素
    factors: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        comment="影响因素权重(JSON)"
    )

    # 建议
    recommendations: Mapped[list] = mapped_column(
        JSONB,
        nullable=True,
        comment="建议列表(JSON)"
    )

    # 验证数据 (实际精力vs预测精力)
    actual_energy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="实际精力(用于验证预测准确性)"
    )
    prediction_error: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="预测误差(abs(actual - predicted))"
    )

    # 模型版本
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1.0.0-heuristic",
        comment="预测模型版本"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )

    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="energy_predictions"
    )

    # 索引
    __table_args__ = (
        Index('ix_energy_predictions_user_target', 'user_id', 'target_time'),
        Index('ix_energy_predictions_user_predicted', 'user_id', 'predicted_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<EnergyPrediction(id={self.id}, user_id={self.user_id}, "
            f"target={self.target_time}, level={self.energy_level}, score={self.energy_score})>"
        )


class EnergyBaseline(Base):
    """用户个性化精力基线"""

    __tablename__ = "energy_baselines"

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
        unique=True,  # 每个用户一条基线记录
        index=True,
        comment="用户ID"
    )

    # 基线数据
    avg_energy: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="平均精力(1-10)"
    )
    high_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="高精力阈值"
    )
    low_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="低精力阈值"
    )
    optimal_sleep: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=8.0,
        comment="最佳睡眠时长(小时)"
    )

    # 统计数据
    data_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="用于计算基线的数据点数"
    )
    calculation_period_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        comment="计算周期(天)"
    )

    # 时间戳
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="计算时间"
    )
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
        back_populates="energy_baseline"
    )

    def __repr__(self) -> str:
        return (
            f"<EnergyBaseline(id={self.id}, user_id={self.user_id}, "
            f"avg={self.avg_energy:.1f}, optimal_sleep={self.optimal_sleep:.1f})>"
        )


class EnergyPattern(Base):
    """用户精力模式识别结果"""

    __tablename__ = "energy_patterns"

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

    # 模式信息
    pattern_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="模式类型: daily/weekly/monthly"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="模式描述"
    )

    # 模式数据
    peak_hours: Mapped[list] = mapped_column(
        JSONB,
        nullable=True,
        comment="高精力时段(JSON数组)"
    )
    low_hours: Mapped[list] = mapped_column(
        JSONB,
        nullable=True,
        comment="低精力时段(JSON数组)"
    )

    # 置信度和元数据
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="模式置信度(0-1)"
    )
    data_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="用于识别的数据点数"
    )
    pattern_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="详细模式数据(JSON)"
    )

    # 时间戳
    identified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="识别时间"
    )
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
        back_populates="energy_patterns"
    )

    # 索引
    __table_args__ = (
        Index('ix_energy_patterns_user_type', 'user_id', 'pattern_type'),
    )

    def __repr__(self) -> str:
        return (
            f"<EnergyPattern(id={self.id}, user_id={self.user_id}, "
            f"type={self.pattern_type}, confidence={self.confidence:.2f})>"
        )


class EnvironmentData(Base):
    """环境数据(天气、气压等)"""

    __tablename__ = "environment_data"

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

    # 位置信息
    location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="位置(城市名或经纬度)"
    )

    # 环境数据
    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="温度(℃)"
    )
    weather: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="天气状况(晴/阴/雨等)"
    )
    pressure: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="气压(hPa)"
    )
    humidity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="湿度(%)"
    )
    uv_index: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="紫外线指数"
    )
    air_quality: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="空气质量指数(AQI)"
    )

    # 原始数据
    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="API原始数据(JSON)"
    )

    # 数据来源
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="openweather",
        comment="数据来源API"
    )

    # 时间戳
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="采集时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )

    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="environment_data"
    )

    # 索引
    __table_args__ = (
        Index('ix_environment_data_location_recorded', 'location', 'recorded_at'),
        Index('ix_environment_data_user_recorded', 'user_id', 'recorded_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<EnvironmentData(id={self.id}, user_id={self.user_id}, location={self.location}, "
            f"temp={self.temperature}℃, weather={self.weather})>"
        )
