"""
健康数据分析服务
提供用户健康数据的统计分析功能,用于AI个性化建议
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import health_data as health_crud
from app.models.health_data import HealthDataType


async def get_user_health_summary(
    db: AsyncSession,
    user_id: UUID,
    days: int = 7
) -> Dict[str, Any]:
    """
    获取用户健康数据摘要

    聚合用户最近N天的核心健康指标，用于AI对话上下文

    Args:
        db: 数据库会话
        user_id: 用户ID
        days: 统计天数(默认7天)

    Returns:
        健康数据摘要字典
    """
    summary: Dict[str, Any] = {}

    # 1. 睡眠数据
    sleep_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.SLEEP_DURATION, days
    )
    if sleep_avg is not None:
        summary["sleep_avg"] = round(sleep_avg, 1)
        summary["sleep_status"] = _get_sleep_status(sleep_avg)
    else:
        summary["sleep_avg"] = None
        summary["sleep_status"] = "未知"

    # 2. 心率变异性 (HRV)
    hrv_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.HRV, days
    )
    if hrv_avg is not None:
        summary["hrv_avg"] = round(hrv_avg, 1)
        summary["hrv_status"] = _get_hrv_status(hrv_avg)
    else:
        summary["hrv_avg"] = None
        summary["hrv_status"] = "未知"

    # 3. 步数
    steps_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.STEPS, days
    )
    if steps_avg is not None:
        summary["steps_avg"] = round(steps_avg, 0)
        summary["activity_level"] = _get_activity_level(steps_avg)
    else:
        summary["steps_avg"] = None
        summary["activity_level"] = "未知"

    # 4. 压力水平
    stress_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.STRESS_LEVEL, days
    )
    if stress_avg is not None:
        summary["stress_level"] = round(stress_avg, 1)
        summary["stress_status"] = _get_stress_status(stress_avg)
    else:
        summary["stress_level"] = None
        summary["stress_status"] = "未知"

    # 5. 能量水平(主观评估)
    energy_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.ENERGY_LEVEL, days
    )
    if energy_avg is not None:
        summary["energy_level"] = round(energy_avg, 1)
        summary["energy_status"] = _get_energy_status(energy_avg)
    else:
        summary["energy_level"] = None
        summary["energy_status"] = "未知"

    # 6. 静息心率
    resting_hr_avg = await health_crud.get_health_data_average(
        db, user_id, HealthDataType.HEART_RATE_RESTING, days
    )
    if resting_hr_avg is not None:
        summary["resting_heart_rate_avg"] = round(resting_hr_avg, 0)

    # 7. 数据完整性评分 (有数据的指标数量)
    data_count = sum(1 for v in [sleep_avg, hrv_avg, steps_avg, stress_avg, energy_avg] if v is not None)
    summary["data_completeness"] = f"{data_count}/5"

    return summary


def _get_sleep_status(avg_hours: float) -> str:
    """评估睡眠状态"""
    if avg_hours < 6:
        return "严重不足"
    elif avg_hours < 7:
        return "略显不足"
    elif avg_hours <= 8:
        return "良好"
    elif avg_hours <= 9:
        return "充足"
    else:
        return "偏多"


def _get_hrv_status(hrv_value: float) -> str:
    """评估HRV状态 (单位:ms)"""
    if hrv_value < 30:
        return "较低"
    elif hrv_value < 50:
        return "一般"
    elif hrv_value <= 70:
        return "良好"
    else:
        return "优秀"


def _get_activity_level(avg_steps: float) -> str:
    """评估活动水平"""
    if avg_steps < 3000:
        return "久坐"
    elif avg_steps < 5000:
        return "轻度活动"
    elif avg_steps < 8000:
        return "中度活动"
    elif avg_steps < 10000:
        return "活跃"
    else:
        return "非常活跃"


def _get_stress_status(stress_value: float) -> str:
    """评估压力状态 (1-100)"""
    if stress_value < 30:
        return "低压力"
    elif stress_value < 50:
        return "轻度压力"
    elif stress_value < 70:
        return "中度压力"
    else:
        return "高压力"


def _get_energy_status(energy_value: float) -> str:
    """评估能量状态 (1-10)"""
    if energy_value < 3:
        return "疲惫"
    elif energy_value < 5:
        return "略显疲劳"
    elif energy_value <= 7:
        return "正常"
    elif energy_value <= 9:
        return "充沛"
    else:
        return "精力旺盛"


async def get_latest_metrics(
    db: AsyncSession,
    user_id: UUID
) -> Dict[str, Optional[float]]:
    """
    获取最新的健康指标数据

    返回各类型最新一次记录的数值

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        最新指标字典
    """
    metrics = {}

    key_types = [
        HealthDataType.SLEEP_DURATION,
        HealthDataType.HRV,
        HealthDataType.STEPS,
        HealthDataType.STRESS_LEVEL,
        HealthDataType.ENERGY_LEVEL,
        HealthDataType.MOOD,
        HealthDataType.FOCUS
    ]

    for data_type in key_types:
        latest = await health_crud.get_latest_health_data(db, user_id, data_type)
        metrics[data_type] = latest.value if latest else None

    return metrics


async def get_trend_analysis(
    db: AsyncSession,
    user_id: UUID,
    data_type: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    分析特定指标的趋势

    计算趋势方向、变化率等

    Args:
        db: 数据库会话
        user_id: 用户ID
        data_type: 数据类型
        days: 分析天数

    Returns:
        趋势分析结果
    """
    # 获取最近N天的数据
    data_list = await health_crud.get_health_data_by_type(
        db=db,
        user_id=user_id,
        data_type=data_type,
        start_date=datetime.utcnow() - timedelta(days=days),
        end_date=datetime.utcnow(),
        limit=1000
    )

    if len(data_list) < 2:
        return {
            "trend": "insufficient_data",
            "data_points": len(data_list)
        }

    # 简单线性趋势分析
    values = [d.value for d in data_list]
    first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
    second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

    change_percent = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0

    # 判断趋势
    if abs(change_percent) < 5:
        trend = "stable"
    elif change_percent > 0:
        trend = "improving" if data_type in [
            HealthDataType.SLEEP_DURATION,
            HealthDataType.HRV,
            HealthDataType.STEPS,
            HealthDataType.ENERGY_LEVEL
        ] else "worsening"
    else:
        trend = "worsening" if data_type in [
            HealthDataType.SLEEP_DURATION,
            HealthDataType.HRV,
            HealthDataType.STEPS,
            HealthDataType.ENERGY_LEVEL
        ] else "improving"

    return {
        "trend": trend,
        "change_percent": round(change_percent, 1),
        "first_period_avg": round(first_half_avg, 2),
        "second_period_avg": round(second_half_avg, 2),
        "data_points": len(data_list)
    }
