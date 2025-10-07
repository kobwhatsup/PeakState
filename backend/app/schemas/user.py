"""
用户相关Pydantic模式
用于请求验证和响应序列化
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re


class UserRegister(BaseModel):
    """用户注册请求"""
    phone_number: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="手机号(11位)"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="密码(6-50位)"
    )
    coach_selection: str = Field(
        default="coach",
        description="AI教练类型(mentor/coach/doctor/zen)"
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("coach_selection")
    @classmethod
    def validate_coach_type(cls, v: str) -> str:
        """验证教练类型"""
        valid_types = ["sage", "companion", "expert", "mentor", "coach", "doctor", "zen"]
        if v not in valid_types:
            raise ValueError(f"教练类型必须是以下之一: {', '.join(valid_types)}")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    phone_number: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新"""
    coach_selection: Optional[str] = Field(None, description="AI教练类型")
    timezone: Optional[str] = Field(None, description="时区")
    morning_briefing_enabled: Optional[bool] = Field(None, description="是否启用早报")
    morning_briefing_time: Optional[str] = Field(None, description="早报时间(HH:MM)")
    evening_review_enabled: Optional[bool] = Field(None, description="是否启用晚间复盘")
    evening_review_time: Optional[str] = Field(None, description="晚间复盘时间(HH:MM)")

    @field_validator("morning_briefing_time", "evening_review_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """验证时间格式"""
        if v is None:
            return v
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
            raise ValueError("时间格式必须是HH:MM(例如: 07:00)")
        return v


class UserResponse(BaseModel):
    """用户信息响应"""
    id: UUID = Field(..., description="用户ID")
    phone_number: str = Field(..., description="手机号")
    coach_selection: str = Field(..., description="AI教练类型")
    timezone: str = Field(..., description="时区")

    # 订阅状态
    is_subscribed: bool = Field(..., description="是否已订阅")
    subscription_type: Optional[str] = Field(None, description="订阅类型")
    subscription_end_date: Optional[datetime] = Field(None, description="订阅到期时间")

    # 试用状态
    is_trial: bool = Field(..., description="是否试用中")
    trial_end_date: Optional[datetime] = Field(None, description="试用到期时间")

    # 用户偏好
    morning_briefing_enabled: bool = Field(..., description="是否启用早报")
    morning_briefing_time: str = Field(..., description="早报时间")
    evening_review_enabled: bool = Field(..., description="是否启用晚间复盘")
    evening_review_time: str = Field(..., description="晚间复盘时间")

    # 时间戳
    created_at: datetime = Field(..., description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

    model_config = {
        "from_attributes": True  # 允许从ORM模型创建
    }


class UserSimple(BaseModel):
    """简化的用户信息(用于列表展示)"""
    id: UUID = Field(..., description="用户ID")
    phone_number: str = Field(..., description="手机号")
    coach_selection: str = Field(..., description="AI教练类型")
    is_subscribed: bool = Field(..., description="是否已订阅")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {
        "from_attributes": True
    }
