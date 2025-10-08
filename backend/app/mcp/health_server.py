"""
MCP Health Server
提供健康数据查询工具，供AI调用
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.health_data import (
    get_health_data_by_type,
    get_health_data_average,
    get_latest_health_data
)
from app.models.health_data import HealthDataType
from app.mcp.base import get_global_registry
from app.mcp.schemas import (
    READ_SLEEP_DATA_SCHEMA,
    READ_HRV_DATA_SCHEMA,
    READ_ACTIVITY_SUMMARY_SCHEMA,
    ANALYZE_ENERGY_TREND_SCHEMA
)

logger = logging.getLogger(__name__)


# ============ 工具实现函数 ============

async def read_sleep_data(
    days: int = 7,
    user_id: Optional[UUID] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    读取用户睡眠数据

    Args:
        days: 查询天数
        user_id: 用户ID (由context传入)
        db: 数据库会话 (由context传入)

    Returns:
        {
            "average_duration": 7.2,  # 平均睡眠时长(小时)
            "total_records": 6,  # 数据点数量
            "data_points": [
                {
                    "date": "2025-10-01",
                    "duration_hours": 7.5,
                    "recorded_at": "2025-10-01T08:30:00"
                },
                ...
            ],
            "trend": "improving",  # improving/stable/declining
            "period_days": 7
        }
    """
    if not user_id or not db:
        return {"error": "Missing user_id or db context"}

    try:
        # 获取睡眠时长数据
        start_date = datetime.utcnow() - timedelta(days=days)
        sleep_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.SLEEP_DURATION,
            start_date=start_date,
            limit=days
        )

        if not sleep_data:
            return {
                "message": f"No sleep data found in the last {days} days",
                "average_duration": 0,
                "total_records": 0,
                "data_points": [],
                "trend": "no_data",
                "period_days": days
            }

        # 计算平均值
        total_hours = sum([d.value for d in sleep_data])
        average_duration = total_hours / len(sleep_data)

        # 格式化数据点
        data_points = [
            {
                "date": d.recorded_at.strftime("%Y-%m-%d"),
                "duration_hours": round(d.value, 2),
                "recorded_at": d.recorded_at.isoformat()
            }
            for d in sleep_data
        ]

        # 计算趋势
        trend = _calculate_trend(sleep_data)

        return {
            "average_duration": round(average_duration, 2),
            "total_records": len(sleep_data),
            "data_points": data_points,
            "trend": trend,
            "period_days": days,
            "unit": "hours"
        }

    except Exception as e:
        logger.error(f"Error reading sleep data: {e}", exc_info=True)
        return {"error": str(e)}


async def read_hrv_data(
    days: int = 7,
    user_id: Optional[UUID] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    读取HRV(心率变异性)数据

    Returns:
        {
            "average_hrv": 65.3,  # 平均HRV(ms)
            "average_resting_hr": 58,  # 平均静息心率
            "total_records": 6,
            "data_points": [...],
            "recovery_score": 8.2,  # 恢复评分(0-10)
            "trend": "improving"
        }
    """
    if not user_id or not db:
        return {"error": "Missing user_id or db context"}

    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # 获取HRV数据
        hrv_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.HRV,
            start_date=start_date,
            limit=days
        )

        # 获取静息心率数据
        hr_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE_RESTING,
            start_date=start_date,
            limit=days
        )

        if not hrv_data and not hr_data:
            return {
                "message": f"No HRV data found in the last {days} days",
                "average_hrv": 0,
                "average_resting_hr": 0,
                "total_records": 0,
                "data_points": [],
                "recovery_score": 0,
                "trend": "no_data",
                "period_days": days
            }

        # 计算平均HRV
        average_hrv = 0
        if hrv_data:
            total_hrv = sum([d.value for d in hrv_data])
            average_hrv = total_hrv / len(hrv_data)

        # 计算平均静息心率
        average_resting_hr = 0
        if hr_data:
            total_hr = sum([d.value for d in hr_data])
            average_resting_hr = total_hr / len(hr_data)

        # 计算恢复评分 (基于HRV，简化算法)
        recovery_score = _calculate_recovery_score(average_hrv, average_resting_hr)

        # 格式化数据点
        data_points = []
        for d in hrv_data:
            data_points.append({
                "date": d.recorded_at.strftime("%Y-%m-%d"),
                "hrv_ms": round(d.value, 1),
                "recorded_at": d.recorded_at.isoformat()
            })

        # 计算趋势
        trend = _calculate_trend(hrv_data) if hrv_data else "no_data"

        return {
            "average_hrv": round(average_hrv, 1),
            "average_resting_hr": round(average_resting_hr, 0),
            "total_records": len(hrv_data),
            "data_points": data_points,
            "recovery_score": round(recovery_score, 1),
            "trend": trend,
            "period_days": days,
            "unit": "ms"
        }

    except Exception as e:
        logger.error(f"Error reading HRV data: {e}", exc_info=True)
        return {"error": str(e)}


async def read_activity_summary(
    date: str = "today",
    user_id: Optional[UUID] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    读取活动摘要

    Args:
        date: 查询日期 (today/yesterday/YYYY-MM-DD)

    Returns:
        {
            "date": "2025-10-07",
            "steps": 8542,
            "calories": 2150,
            "active_minutes": 45,
            "distance_km": 6.2,
            "has_data": true
        }
    """
    if not user_id or not db:
        return {"error": "Missing user_id or db context"}

    try:
        # 解析日期
        if date == "today":
            target_date = datetime.utcnow().date()
        elif date == "yesterday":
            target_date = (datetime.utcnow() - timedelta(days=1)).date()
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()

        # 查询当天数据
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # 获取步数
        steps_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.STEPS,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=10
        )

        # 获取卡路里
        calories_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.CALORIES_BURNED,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=10
        )

        # 获取活跃时长
        active_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.ACTIVE_MINUTES,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=10
        )

        # 汇总数据
        total_steps = sum([d.value for d in steps_data]) if steps_data else 0
        total_calories = sum([d.value for d in calories_data]) if calories_data else 0
        total_active_minutes = sum([d.value for d in active_data]) if active_data else 0

        # 估算距离 (步数 * 0.0007 km/步)
        distance_km = total_steps * 0.0007

        has_data = bool(steps_data or calories_data or active_data)

        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "steps": round(total_steps, 0),
            "calories": round(total_calories, 0),
            "active_minutes": round(total_active_minutes, 0),
            "distance_km": round(distance_km, 2),
            "has_data": has_data
        }

    except Exception as e:
        logger.error(f"Error reading activity summary: {e}", exc_info=True)
        return {"error": str(e)}


async def analyze_energy_trend(
    days: int = 7,
    user_id: Optional[UUID] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    分析能量趋势

    Returns:
        {
            "average_energy": 7.2,  # 平均能量水平(0-10)
            "peak_hours": ["09:00-11:00", "15:00-17:00"],
            "low_hours": ["14:00-15:00", "22:00-23:00"],
            "total_records": 6,
            "factors": {
                "sleep_impact": 0.8,  # 睡眠影响权重
                "activity_impact": 0.5,
                "stress_impact": -0.3
            },
            "trend": "improving"
        }
    """
    if not user_id or not db:
        return {"error": "Missing user_id or db context"}

    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # 获取能量水平数据
        energy_data = await get_health_data_by_type(
            db=db,
            user_id=user_id,
            data_type=HealthDataType.ENERGY_LEVEL,
            start_date=start_date,
            limit=days * 5  # 每天可能多次记录
        )

        if not energy_data:
            return {
                "message": f"No energy data found in the last {days} days",
                "average_energy": 0,
                "peak_hours": [],
                "low_hours": [],
                "total_records": 0,
                "factors": {},
                "trend": "no_data",
                "period_days": days
            }

        # 计算平均能量
        total_energy = sum([d.value for d in energy_data])
        average_energy = total_energy / len(energy_data)

        # 分析时间段分布
        hourly_energy = {}
        for d in energy_data:
            hour = d.recorded_at.hour
            if hour not in hourly_energy:
                hourly_energy[hour] = []
            hourly_energy[hour].append(d.value)

        # 计算每小时平均能量
        hourly_avg = {
            hour: sum(values) / len(values)
            for hour, values in hourly_energy.items()
        }

        # 找出高峰和低谷时段
        sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [f"{h:02d}:00-{h+1:02d}:00" for h, _ in sorted_hours[:2]]
        low_hours = [f"{h:02d}:00-{h+1:02d}:00" for h, _ in sorted_hours[-2:]]

        # 分析影响因素
        sleep_avg = await get_health_data_average(
            db, user_id, HealthDataType.SLEEP_DURATION, days
        )
        stress_avg = await get_health_data_average(
            db, user_id, HealthDataType.STRESS_LEVEL, days
        )

        factors = {}
        if sleep_avg:
            # 7-9小时睡眠为最佳，计算偏离度
            sleep_impact = 1.0 - abs(sleep_avg - 8.0) / 8.0
            factors["sleep_impact"] = round(sleep_impact, 2)

        if stress_avg:
            # 压力越高，影响越负面
            stress_impact = -(stress_avg / 10.0)
            factors["stress_impact"] = round(stress_impact, 2)

        # 计算趋势
        trend = _calculate_trend(energy_data)

        return {
            "average_energy": round(average_energy, 1),
            "peak_hours": peak_hours,
            "low_hours": low_hours,
            "total_records": len(energy_data),
            "factors": factors,
            "trend": trend,
            "period_days": days,
            "unit": "score (0-10)"
        }

    except Exception as e:
        logger.error(f"Error analyzing energy trend: {e}", exc_info=True)
        return {"error": str(e)}


# ============ 辅助函数 ============

def _calculate_trend(data_list: List) -> str:
    """
    计算趋势：improving/stable/declining

    使用简单的前后半段对比算法
    """
    if len(data_list) < 3:
        return "insufficient_data"

    mid_point = len(data_list) // 2
    first_half = data_list[:mid_point]
    second_half = data_list[mid_point:]

    avg_first = sum([d.value for d in first_half]) / len(first_half)
    avg_second = sum([d.value for d in second_half]) / len(second_half)

    diff_percent = ((avg_second - avg_first) / avg_first) * 100

    if diff_percent > 5:
        return "improving"
    elif diff_percent < -5:
        return "declining"
    else:
        return "stable"


def _calculate_recovery_score(avg_hrv: float, avg_resting_hr: float) -> float:
    """
    计算恢复评分 (0-10)

    基于HRV和静息心率的简化算法：
    - HRV越高越好 (正常范围20-100ms)
    - 静息心率越低越好 (正常范围50-80bpm)
    """
    # HRV评分 (0-5分)
    hrv_score = min(5.0, (avg_hrv / 20.0))

    # 心率评分 (0-5分，心率越低越好)
    hr_score = max(0, 5.0 - ((avg_resting_hr - 50) / 6.0))

    total_score = hrv_score + hr_score

    return min(10.0, max(0.0, total_score))


# ============ 工具注册 ============

def register_health_tools():
    """注册所有健康数据工具到全局注册表"""
    registry = get_global_registry()

    # 工具1: 读取睡眠数据
    registry.register_function(
        name="read_sleep_data",
        description="读取用户的睡眠数据，包括平均睡眠时长、数据点和趋势分析。用于回答关于睡眠质量和睡眠模式的问题。",
        input_schema=READ_SLEEP_DATA_SCHEMA,
        handler=read_sleep_data
    )

    # 工具2: 读取HRV数据
    registry.register_function(
        name="read_hrv_data",
        description="读取用户的心率变异性(HRV)数据，包括平均HRV、静息心率和恢复评分。用于评估用户的压力水平和恢复状态。",
        input_schema=READ_HRV_DATA_SCHEMA,
        handler=read_hrv_data
    )

    # 工具3: 读取活动摘要
    registry.register_function(
        name="read_activity_summary",
        description="读取用户指定日期的活动摘要，包括步数、消耗卡路里、活跃时长和距离。用于回答关于日常活动量的问题。",
        input_schema=READ_ACTIVITY_SUMMARY_SCHEMA,
        handler=read_activity_summary
    )

    # 工具4: 分析能量趋势
    registry.register_function(
        name="analyze_energy_trend",
        description="分析用户的能量水平趋势，识别高峰和低谷时段，并分析睡眠和压力等影响因素。用于生成个性化的能量管理建议。",
        input_schema=ANALYZE_ENERGY_TREND_SCHEMA,
        handler=analyze_energy_trend
    )

    logger.info(f"✅ Registered {len(registry)} health tools")


# 自动注册
register_health_tools()
