"""
天气数据服务

用于获取环境数据（天气、温度、气压、湿度、空气质量等）
支持OpenWeather API和和风天气API
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.energy import EnvironmentData
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WeatherService:
    """天气数据服务"""

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.provider = settings.WEATHER_PROVIDER  # 'openweather' or 'qweather'
        self.timeout = 10.0

    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        获取当前天气数据

        Args:
            location: 位置（城市名或经纬度）

        Returns:
            天气数据字典
        """
        try:
            if self.provider == 'openweather':
                return await self._get_openweather_data(location)
            elif self.provider == 'qweather':
                return await self._get_qweather_data(location)
            else:
                logger.error(f"不支持的天气服务提供商: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"获取天气数据失败: {e}")
            return None

    async def _get_openweather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        从OpenWeather API获取数据

        文档: https://openweathermap.org/api
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 如果是城市名
                if ',' not in location or not self._is_coordinates(location):
                    url = "https://api.openweathermap.org/data/2.5/weather"
                    params = {
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric",  # 摄氏度
                        "lang": "zh_cn"
                    }
                else:
                    # 如果是经纬度 (lat,lon)
                    lat, lon = location.split(',')
                    url = "https://api.openweathermap.org/data/2.5/weather"
                    params = {
                        "lat": lat.strip(),
                        "lon": lon.strip(),
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "zh_cn"
                    }

                # 获取当前天气
                response = await client.get(url, params=params)
                response.raise_for_status()
                weather_data = response.json()

                # 获取空气质量数据
                air_quality = None
                if 'coord' in weather_data:
                    lat = weather_data['coord']['lat']
                    lon = weather_data['coord']['lon']
                    aqi_url = "https://api.openweathermap.org/data/2.5/air_pollution"
                    aqi_params = {
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key
                    }
                    aqi_response = await client.get(aqi_url, params=aqi_params)
                    if aqi_response.status_code == 200:
                        aqi_data = aqi_response.json()
                        if 'list' in aqi_data and len(aqi_data['list']) > 0:
                            air_quality = aqi_data['list'][0]['main']['aqi']

                # 转换为标准格式
                return {
                    'location': weather_data.get('name', location),
                    'temperature': weather_data['main']['temp'],
                    'feels_like': weather_data['main']['feels_like'],
                    'weather': weather_data['weather'][0]['description'],
                    'weather_code': weather_data['weather'][0]['id'],
                    'pressure': weather_data['main']['pressure'],
                    'humidity': weather_data['main']['humidity'],
                    'air_quality': air_quality,
                    'wind_speed': weather_data['wind']['speed'],
                    'clouds': weather_data['clouds']['all'],
                    'visibility': weather_data.get('visibility'),
                    'timestamp': datetime.fromtimestamp(weather_data['dt'])
                }

        except httpx.HTTPError as e:
            logger.error(f"OpenWeather API请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析OpenWeather数据失败: {e}")
            return None

    async def _get_qweather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        从和风天气API获取数据

        文档: https://dev.qweather.com/docs/api/
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 先获取城市ID（如果是城市名）
                location_id = location
                if not location.isdigit() and not self._is_coordinates(location):
                    # 搜索城市
                    search_url = "https://geoapi.qweather.com/v2/city/lookup"
                    search_params = {
                        "location": location,
                        "key": self.api_key,
                        "lang": "zh"
                    }
                    search_response = await client.get(search_url, params=search_params)
                    search_response.raise_for_status()
                    search_data = search_response.json()

                    if search_data['code'] != '200' or not search_data.get('location'):
                        logger.error(f"找不到城市: {location}")
                        return None

                    location_id = search_data['location'][0]['id']

                # 获取实时天气
                weather_url = "https://devapi.qweather.com/v7/weather/now"
                weather_params = {
                    "location": location_id,
                    "key": self.api_key,
                    "lang": "zh"
                }
                weather_response = await client.get(weather_url, params=weather_params)
                weather_response.raise_for_status()
                weather_data = weather_response.json()

                if weather_data['code'] != '200':
                    logger.error(f"获取天气数据失败: {weather_data}")
                    return None

                now = weather_data['now']

                # 获取空气质量
                air_quality = None
                air_url = "https://devapi.qweather.com/v7/air/now"
                air_params = {
                    "location": location_id,
                    "key": self.api_key,
                    "lang": "zh"
                }
                air_response = await client.get(air_url, params=air_params)
                if air_response.status_code == 200:
                    air_data = air_response.json()
                    if air_data['code'] == '200' and 'now' in air_data:
                        air_quality = int(air_data['now']['aqi'])

                # 转换为标准格式
                return {
                    'location': location,
                    'temperature': float(now['temp']),
                    'feels_like': float(now['feelsLike']),
                    'weather': now['text'],
                    'weather_code': int(now['icon']),
                    'pressure': float(now['pressure']),
                    'humidity': int(now['humidity']),
                    'air_quality': air_quality,
                    'wind_speed': float(now['windSpeed']),
                    'clouds': int(now['cloud']),
                    'visibility': int(now['vis']),
                    'timestamp': datetime.fromisoformat(now['obsTime'])
                }

        except httpx.HTTPError as e:
            logger.error(f"和风天气API请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析和风天气数据失败: {e}")
            return None

    def _is_coordinates(self, location: str) -> bool:
        """判断是否为经纬度坐标"""
        try:
            parts = location.split(',')
            if len(parts) != 2:
                return False
            float(parts[0].strip())
            float(parts[1].strip())
            return True
        except ValueError:
            return False

    async def save_environment_data(
        self,
        db: AsyncSession,
        user_id: str,
        weather_data: Dict[str, Any]
    ) -> Optional[EnvironmentData]:
        """
        保存环境数据到数据库

        Args:
            db: 数据库会话
            user_id: 用户ID
            weather_data: 天气数据

        Returns:
            保存的环境数据记录
        """
        try:
            env_data = EnvironmentData(
                user_id=user_id,
                location=weather_data['location'],
                temperature=weather_data['temperature'],
                weather=weather_data['weather'],
                pressure=weather_data['pressure'],
                humidity=weather_data['humidity'],
                air_quality=weather_data.get('air_quality'),
                recorded_at=weather_data.get('timestamp', datetime.utcnow())
            )

            db.add(env_data)
            await db.commit()
            await db.refresh(env_data)

            logger.info(f"保存环境数据成功: user_id={user_id}, location={weather_data['location']}")
            return env_data

        except Exception as e:
            logger.error(f"保存环境数据失败: {e}")
            await db.rollback()
            return None

    async def get_latest_environment_data(
        self,
        db: AsyncSession,
        user_id: str,
        hours: int = 24
    ) -> list[EnvironmentData]:
        """
        获取用户最近的环境数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            hours: 获取最近多少小时的数据

        Returns:
            环境数据列表
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            result = await db.execute(
                select(EnvironmentData)
                .where(EnvironmentData.user_id == user_id)
                .where(EnvironmentData.recorded_at >= since)
                .order_by(EnvironmentData.recorded_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"获取环境数据失败: {e}")
            return []

    async def collect_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        location: str
    ) -> Optional[EnvironmentData]:
        """
        采集并保存环境数据（组合操作）

        Args:
            db: 数据库会话
            user_id: 用户ID
            location: 位置

        Returns:
            保存的环境数据记录
        """
        weather_data = await self.get_current_weather(location)
        if not weather_data:
            return None

        return await self.save_environment_data(db, user_id, weather_data)


# 单例实例
_weather_service: Optional[WeatherService] = None


async def get_weather_service() -> WeatherService:
    """获取天气服务单例"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
