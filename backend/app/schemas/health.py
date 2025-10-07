"""
健康数据Pydantic模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class HealthDataCreate(BaseModel):
    """创建健康数据请求"""
    data_type: str = Field(..., description="数据类型(如sleep_duration, hrv等)")
    value: float = Field(..., description="数据值")
    source: Optional[str] = Field(None, description="数据来源")
    unit: Optional[str] = Field(None, description="单位")
    recorded_at: Optional[datetime] = Field(None, description="数据采集时间")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    external_id: Optional[str] = Field(None, description="外部系统ID")

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        """验证数据值"""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v


class HealthDataBatchCreate(BaseModel):
    """批量创建健康数据请求"""
    data: List[HealthDataCreate] = Field(..., description="健康数据列表")

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: List[HealthDataCreate]) -> List[HealthDataCreate]:
        """验证数据列表"""
        if len(v) == 0:
            raise ValueError("Data list cannot be empty")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 items per batch")
        return v


class HealthDataResponse(BaseModel):
    """健康数据响应"""
    id: UUID
    user_id: UUID
    data_type: str
    value: float
    unit: Optional[str] = None
    source: str
    recorded_at: datetime
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthDataListResponse(BaseModel):
    """健康数据列表响应"""
    data: List[HealthDataResponse]
    total: int
    data_type: str


class HealthSummaryResponse(BaseModel):
    """健康数据摘要响应"""
    user_id: UUID
    period_days: int
    summary: Dict[str, Any] = Field(
        ...,
        description="健康数据摘要,键为数据类型,值为{average, period_days}"
    )
    generated_at: datetime
