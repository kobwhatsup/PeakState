"""
健康数据CRUD操作
提供健康数据的增删改查功能
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_data import HealthData, HealthDataType, HealthDataSource


async def create_health_data(
    db: AsyncSession,
    user_id: UUID,
    data_type: str,
    value: float,
    source: str = HealthDataSource.MANUAL,
    unit: Optional[str] = None,
    recorded_at: Optional[datetime] = None,
    extra_data: Optional[Dict] = None,
    external_id: Optional[str] = None
) -> HealthData:
    """
    创建单条健康数据

    Args:
        db: 数据库会话
        user_id: 用户ID
        data_type: 数据类型(如sleep_duration, hrv等)
        value: 数据值
        source: 数据来源
        unit: 单位
        recorded_at: 数据采集时间(默认当前时间)
        extra_data: 额外元数据
        external_id: 外部系统ID(防重复)

    Returns:
        创建的健康数据对象
    """
    health_data = HealthData(
        user_id=user_id,
        data_type=data_type,
        value=value,
        source=source,
        unit=unit,
        recorded_at=recorded_at or datetime.utcnow(),
        extra_data=extra_data,
        external_id=external_id,
        synced_at=datetime.utcnow()
    )

    db.add(health_data)
    await db.commit()
    await db.refresh(health_data)

    return health_data


async def create_health_data_batch(
    db: AsyncSession,
    health_data_list: List[HealthData]
) -> List[HealthData]:
    """
    批量创建健康数据

    Args:
        db: 数据库会话
        health_data_list: 健康数据对象列表

    Returns:
        创建的健康数据列表
    """
    db.add_all(health_data_list)
    await db.commit()

    # 刷新所有对象
    for data in health_data_list:
        await db.refresh(data)

    return health_data_list


async def get_health_data_by_id(
    db: AsyncSession,
    data_id: UUID,
    user_id: UUID
) -> Optional[HealthData]:
    """
    根据ID获取健康数据

    Args:
        db: 数据库会话
        data_id: 数据ID
        user_id: 用户ID(权限验证)

    Returns:
        健康数据对象或None
    """
    query = select(HealthData).where(
        and_(
            HealthData.id == data_id,
            HealthData.user_id == user_id
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_health_data_by_type(
    db: AsyncSession,
    user_id: UUID,
    data_type: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> List[HealthData]:
    """
    获取指定类型的健康数据

    Args:
        db: 数据库会话
        user_id: 用户ID
        data_type: 数据类型
        start_date: 开始日期(默认30天前)
        end_date: 结束日期(默认当前)
        limit: 最大返回数量

    Returns:
        健康数据列表
    """
    if start_date is None:
        start_date = datetime.utcnow() - timedelta(days=30)
    if end_date is None:
        end_date = datetime.utcnow()

    query = select(HealthData).where(
        and_(
            HealthData.user_id == user_id,
            HealthData.data_type == data_type,
            HealthData.recorded_at >= start_date,
            HealthData.recorded_at <= end_date
        )
    ).order_by(desc(HealthData.recorded_at)).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_latest_health_data(
    db: AsyncSession,
    user_id: UUID,
    data_type: str
) -> Optional[HealthData]:
    """
    获取最新的健康数据

    Args:
        db: 数据库会话
        user_id: 用户ID
        data_type: 数据类型

    Returns:
        最新的健康数据或None
    """
    query = select(HealthData).where(
        and_(
            HealthData.user_id == user_id,
            HealthData.data_type == data_type
        )
    ).order_by(desc(HealthData.recorded_at)).limit(1)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_health_data_average(
    db: AsyncSession,
    user_id: UUID,
    data_type: str,
    days: int = 7
) -> Optional[float]:
    """
    计算健康数据平均值

    Args:
        db: 数据库会话
        user_id: 用户ID
        data_type: 数据类型
        days: 天数(默认7天)

    Returns:
        平均值或None
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    query = select(func.avg(HealthData.value)).where(
        and_(
            HealthData.user_id == user_id,
            HealthData.data_type == data_type,
            HealthData.recorded_at >= start_date
        )
    )

    result = await db.execute(query)
    avg_value = result.scalar_one_or_none()

    return float(avg_value) if avg_value is not None else None


async def get_health_summary(
    db: AsyncSession,
    user_id: UUID,
    days: int = 7
) -> Dict[str, Any]:
    """
    获取健康数据摘要

    Args:
        db: 数据库会话
        user_id: 用户ID
        days: 天数(默认7天)

    Returns:
        健康数据摘要字典
    """
    summary = {}

    # 主要数据类型
    key_types = [
        HealthDataType.SLEEP_DURATION,
        HealthDataType.HRV,
        HealthDataType.HEART_RATE_RESTING,
        HealthDataType.STEPS,
        HealthDataType.ENERGY_LEVEL,
        HealthDataType.STRESS_LEVEL
    ]

    for data_type in key_types:
        avg_value = await get_health_data_average(db, user_id, data_type, days)
        if avg_value is not None:
            summary[data_type] = {
                "average": round(avg_value, 2),
                "period_days": days
            }

    return summary


async def update_health_data(
    db: AsyncSession,
    data_id: UUID,
    user_id: UUID,
    **update_fields
) -> Optional[HealthData]:
    """
    更新健康数据

    Args:
        db: 数据库会话
        data_id: 数据ID
        user_id: 用户ID
        **update_fields: 要更新的字段

    Returns:
        更新后的健康数据或None
    """
    health_data = await get_health_data_by_id(db, data_id, user_id)

    if not health_data:
        return None

    # 更新字段
    for field, value in update_fields.items():
        if hasattr(health_data, field):
            setattr(health_data, field, value)

    await db.commit()
    await db.refresh(health_data)

    return health_data


async def delete_health_data(
    db: AsyncSession,
    data_id: UUID,
    user_id: UUID
) -> bool:
    """
    删除健康数据

    Args:
        db: 数据库会话
        data_id: 数据ID
        user_id: 用户ID

    Returns:
        是否删除成功
    """
    health_data = await get_health_data_by_id(db, data_id, user_id)

    if not health_data:
        return False

    await db.delete(health_data)
    await db.commit()

    return True


async def check_duplicate_sync(
    db: AsyncSession,
    user_id: UUID,
    external_id: str
) -> bool:
    """
    检查外部数据是否已同步

    Args:
        db: 数据库会话
        user_id: 用户ID
        external_id: 外部系统ID

    Returns:
        是否已存在
    """
    query = select(HealthData).where(
        and_(
            HealthData.user_id == user_id,
            HealthData.external_id == external_id
        )
    ).limit(1)

    result = await db.execute(query)
    return result.scalar_one_or_none() is not None
