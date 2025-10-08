"""
环境数据上报API路由
接收前端上报的环境数据并存储，用于精力预测和分析
"""

import logging
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.models.energy import EnvironmentData
from app.api.dependencies import get_current_active_user
from app.services.weather import get_weather_service
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Request/Response Models ============

class EnvironmentReportRequest(BaseModel):
    """环境数据上报请求"""
    temperature: float = Field(..., description="温度(°C)")
    weather: str = Field(..., description="天气状况")
    pressure: float = Field(..., description="气压(hPa)")
    humidity: int = Field(..., description="湿度(%)", ge=0, le=100)
    air_quality: int | None = Field(None, description="空气质量指数(AQI)")
    location: str = Field(..., description="位置名称(仅城市级别)")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 25.3,
                "weather": "晴",
                "pressure": 1013.2,
                "humidity": 60,
                "air_quality": 50,
                "location": "北京"
            }
        }


class EnvironmentReportResponse(BaseModel):
    """环境数据上报响应"""
    id: str
    user_id: str
    temperature: float
    weather: str
    pressure: float
    humidity: int
    air_quality: int | None
    location: str
    recorded_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid",
                "temperature": 25.3,
                "weather": "晴",
                "pressure": 1013.2,
                "humidity": 60,
                "air_quality": 50,
                "location": "北京",
                "recorded_at": "2025-10-08T10:00:00Z"
            }
        }


# ============ API Endpoints ============

@router.post("/report", response_model=EnvironmentReportResponse)
async def report_environment_data(
    request: EnvironmentReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上报环境数据

    前端获取天气数据后，调用此接口将数据存储到后端。
    只传输城市级别的位置信息，保护用户隐私。

    Args:
        request: 环境数据
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        存储确认信息

    Raises:
        HTTPException: 存储失败时抛出
    """
    try:
        logger.info(
            f"用户 {current_user.id} 上报环境数据: "
            f"{request.location} {request.temperature}°C {request.weather}"
        )

        # 创建环境数据记录
        env_data = EnvironmentData(
            user_id=current_user.id,
            location=request.location,
            temperature=request.temperature,
            weather=request.weather,
            pressure=request.pressure,
            humidity=request.humidity,
            air_quality=request.air_quality,
            recorded_at=datetime.utcnow()
        )

        db.add(env_data)
        await db.commit()
        await db.refresh(env_data)

        logger.info(f"环境数据上报成功: ID={env_data.id}")

        return EnvironmentReportResponse(
            id=str(env_data.id),
            user_id=str(env_data.user_id),
            temperature=env_data.temperature,
            weather=env_data.weather,
            pressure=env_data.pressure,
            humidity=env_data.humidity,
            air_quality=env_data.air_quality,
            location=env_data.location,
            recorded_at=env_data.recorded_at
        )

    except Exception as e:
        logger.error(f"环境数据上报失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="环境数据上报失败"
        )


@router.get("/history", response_model=List[EnvironmentReportResponse])
async def get_environment_history(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取环境数据历史记录

    Args:
        hours: 获取最近多少小时的数据，默认24小时
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        环境数据列表

    Raises:
        HTTPException: 查询失败时抛出
    """
    try:
        # 计算起始时间
        since = datetime.utcnow() - timedelta(hours=hours)

        # 查询环境数据
        result = await db.execute(
            select(EnvironmentData)
            .where(EnvironmentData.user_id == current_user.id)
            .where(EnvironmentData.recorded_at >= since)
            .order_by(EnvironmentData.recorded_at.desc())
        )
        env_data_list = list(result.scalars().all())

        logger.info(
            f"用户 {current_user.id} 查询环境数据历史: "
            f"找到 {len(env_data_list)} 条记录(最近{hours}小时)"
        )

        return [
            EnvironmentReportResponse(
                id=str(item.id),
                user_id=str(item.user_id),
                temperature=item.temperature,
                weather=item.weather,
                pressure=item.pressure,
                humidity=item.humidity,
                air_quality=item.air_quality,
                location=item.location,
                recorded_at=item.recorded_at
            )
            for item in env_data_list
        ]

    except Exception as e:
        logger.error(f"查询环境数据历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询环境数据失败"
        )


@router.get("/latest", response_model=EnvironmentReportResponse | None)
async def get_latest_environment_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最新的环境数据

    Args:
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        最新的环境数据记录，如果没有则返回None

    Raises:
        HTTPException: 查询失败时抛出
    """
    try:
        result = await db.execute(
            select(EnvironmentData)
            .where(EnvironmentData.user_id == current_user.id)
            .order_by(EnvironmentData.recorded_at.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if not latest:
            logger.info(f"用户 {current_user.id} 无环境数据记录")
            return None

        logger.info(
            f"用户 {current_user.id} 查询最新环境数据: "
            f"{latest.location} {latest.temperature}°C"
        )

        return EnvironmentReportResponse(
            id=str(latest.id),
            user_id=str(latest.user_id),
            temperature=latest.temperature,
            weather=latest.weather,
            pressure=latest.pressure,
            humidity=latest.humidity,
            air_quality=latest.air_quality,
            location=latest.location,
            recorded_at=latest.recorded_at
        )

    except Exception as e:
        logger.error(f"查询最新环境数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询环境数据失败"
        )
