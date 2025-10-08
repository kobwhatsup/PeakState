"""
天气代理API路由
提供安全的天气数据查询接口，保护API密钥不暴露给前端
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_active_user
from app.services.weather import get_weather_service, WeatherService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Request/Response Models ============

class WeatherRequest(BaseModel):
    """天气查询请求"""
    latitude: float = Field(..., description="纬度", ge=-90, le=90)
    longitude: float = Field(..., description="经度", ge=-180, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 39.9042,
                "longitude": 116.4074
            }
        }


class WeatherResponse(BaseModel):
    """天气查询响应"""
    temperature: float = Field(..., description="温度(°C)")
    feels_like: float = Field(..., description="体感温度(°C)")
    weather: str = Field(..., description="天气状况")
    weather_code: int = Field(..., description="天气代码")
    pressure: float = Field(..., description="气压(hPa)")
    humidity: int = Field(..., description="湿度(%)")
    air_quality: int | None = Field(None, description="空气质量指数(AQI)")
    wind_speed: float = Field(..., description="风速(m/s)")
    clouds: int = Field(..., description="云量(%)")
    visibility: int | None = Field(None, description="能见度(m)")
    location: str = Field(..., description="位置名称(城市)")
    timestamp: str = Field(..., description="数据时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 25.3,
                "feels_like": 24.8,
                "weather": "晴",
                "weather_code": 800,
                "pressure": 1013.2,
                "humidity": 60,
                "air_quality": 50,
                "wind_speed": 3.5,
                "clouds": 20,
                "visibility": 10000,
                "location": "北京",
                "timestamp": "2025-10-08T10:00:00Z"
            }
        }


# ============ API Endpoints ============

@router.post("/current", response_model=WeatherResponse)
async def get_current_weather(
    request: WeatherRequest,
    current_user: User = Depends(get_current_active_user),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    获取当前位置的天气数据

    前端通过Geolocation获取用户GPS位置后，调用此接口获取天气信息。
    后端负责调用第三方天气API，保护API密钥安全。

    Args:
        request: 包含经纬度的请求
        current_user: 当前登录用户
        weather_service: 天气服务实例

    Returns:
        天气数据

    Raises:
        HTTPException: 天气API调用失败时抛出
    """
    try:
        logger.info(
            f"用户 {current_user.id} 请求天气数据: "
            f"lat={request.latitude}, lon={request.longitude}"
        )

        # 调用天气服务
        location_str = f"{request.latitude},{request.longitude}"
        weather_data = await weather_service.get_current_weather(location_str)

        if not weather_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="天气服务暂时不可用，请稍后重试"
            )

        logger.info(
            f"天气数据获取成功: {weather_data.get('location')} "
            f"{weather_data.get('temperature')}°C"
        )

        return WeatherResponse(
            temperature=weather_data['temperature'],
            feels_like=weather_data['feels_like'],
            weather=weather_data['weather'],
            weather_code=weather_data['weather_code'],
            pressure=weather_data['pressure'],
            humidity=weather_data['humidity'],
            air_quality=weather_data.get('air_quality'),
            wind_speed=weather_data['wind_speed'],
            clouds=weather_data['clouds'],
            visibility=weather_data.get('visibility'),
            location=weather_data['location'],
            timestamp=weather_data['timestamp'].isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取天气数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取天气数据失败"
        )
