"""
环境数据采集任务

定时采集天气、温度、气压、湿度、空气质量等环境数据
"""

import logging
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.celery_app import celery_app
from app.core.config import get_settings
from app.models.user import User
from app.services.weather import get_weather_service

logger = logging.getLogger(__name__)
settings = get_settings()


# 创建异步数据库会话
engine = create_async_engine(
    settings.DATABASE_URL,
    **settings.database_pool_config
)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        return session


@celery_app.task(
    name="app.tasks.environment.collect_environment_data_for_all_users",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5分钟后重试
)
def collect_environment_data_for_all_users(self):
    """
    为所有用户采集环境数据

    定时任务：每小时执行一次
    """
    import asyncio

    try:
        # 在Celery worker中运行异步任务
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_collect_environment_data())
        return result
    except Exception as e:
        logger.error(f"采集环境数据失败: {e}")
        # 重试任务
        raise self.retry(exc=e)


async def _collect_environment_data() -> dict:
    """
    内部异步函数：执行实际的环境数据采集

    Returns:
        采集结果统计
    """
    db = await get_db()
    weather_service = await get_weather_service()

    try:
        # 获取所有活跃用户（最近7天有活动的用户）
        active_users = await _get_active_users(db)

        success_count = 0
        fail_count = 0

        for user in active_users:
            try:
                # 获取用户位置（从用户资料或默认位置）
                location = await _get_user_location(user, db)

                if not location:
                    logger.warning(f"用户 {user.id} 没有位置信息，跳过环境数据采集")
                    fail_count += 1
                    continue

                # 采集并保存环境数据
                env_data = await weather_service.collect_and_save(
                    db=db,
                    user_id=str(user.id),
                    location=location
                )

                if env_data:
                    success_count += 1
                    logger.info(f"成功采集用户 {user.id} 的环境数据: {location}")
                else:
                    fail_count += 1
                    logger.warning(f"采集用户 {user.id} 的环境数据失败: {location}")

            except Exception as e:
                fail_count += 1
                logger.error(f"处理用户 {user.id} 环境数据时出错: {e}")

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_users": len(active_users),
            "success_count": success_count,
            "fail_count": fail_count,
            "status": "completed"
        }

        logger.info(f"环境数据采集完成: {result}")
        return result

    finally:
        await db.close()


async def _get_active_users(db: AsyncSession) -> List[User]:
    """
    获取活跃用户列表

    活跃用户定义：最近7天有健康数据记录或对话记录的用户
    """
    from datetime import timedelta

    # 简化版：暂时返回所有用户
    # TODO: 后续根据实际活跃度筛选
    result = await db.execute(
        select(User).where(User.is_active == True).limit(1000)
    )
    users = list(result.scalars().all())

    logger.info(f"找到 {len(users)} 个活跃用户")
    return users


async def _get_user_location(user: User, db: AsyncSession) -> str:
    """
    获取用户位置

    优先级:
    1. 用户个人资料中的城市
    2. 最近一次环境数据的位置
    3. 默认位置（北京）
    """
    # 1. 从用户资料获取
    if hasattr(user, 'city') and user.city:
        return user.city

    # 2. 从最近的环境数据获取
    from app.models.energy import EnvironmentData
    result = await db.execute(
        select(EnvironmentData)
        .where(EnvironmentData.user_id == user.id)
        .order_by(EnvironmentData.recorded_at.desc())
        .limit(1)
    )
    latest_env = result.scalar_one_or_none()
    if latest_env and latest_env.location:
        return latest_env.location

    # 3. 默认位置
    return "Beijing"  # OpenWeather使用英文城市名


@celery_app.task(
    name="app.tasks.environment.collect_environment_data_for_user",
    bind=True,
    max_retries=2
)
def collect_environment_data_for_user(self, user_id: str, location: str = None):
    """
    为单个用户采集环境数据

    可以手动触发，用于用户位置变更时立即更新环境数据

    Args:
        user_id: 用户ID
        location: 位置（可选，如果不提供则从用户资料获取）
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            _collect_user_environment_data(user_id, location)
        )
        return result
    except Exception as e:
        logger.error(f"采集用户 {user_id} 环境数据失败: {e}")
        raise self.retry(exc=e)


async def _collect_user_environment_data(user_id: str, location: str = None) -> dict:
    """内部异步函数：为单个用户采集环境数据"""
    db = await get_db()
    weather_service = await get_weather_service()

    try:
        # 如果没有提供位置，尝试获取用户位置
        if not location:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"用户 {user_id} 不存在")
                return {"status": "failed", "error": "User not found"}

            location = await _get_user_location(user, db)

        # 采集并保存
        env_data = await weather_service.collect_and_save(
            db=db,
            user_id=user_id,
            location=location
        )

        if env_data:
            return {
                "status": "success",
                "user_id": user_id,
                "location": location,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "failed",
                "user_id": user_id,
                "error": "Weather API request failed"
            }

    finally:
        await db.close()
