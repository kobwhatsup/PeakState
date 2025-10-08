"""
精力数字孪生系统 (Energy Digital Twin)
为每个用户构建动态的、多维度的"精力数字孪生"

核心功能:
1. 实时反映用户精力状态
2. 预测未来精力变化
3. 识别个人精力模式
4. 提供个性化建议
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.health_data import HealthData, HealthDataType
from app.ai.energy_prediction import (
    EnergyPredictionModel,
    get_energy_prediction_model,
    EnergyPrediction,
    EnergyLevel
)


@dataclass
class EnergyPattern:
    """精力模式"""
    pattern_type: str  # daily/weekly/monthly
    description: str
    peak_hours: List[int]  # 高精力时段
    low_hours: List[int]   # 低精力时段
    confidence: float


@dataclass
class PersonalBaseline:
    """个性化基线"""
    user_id: str
    avg_energy: float  # 平均精力(1-10)
    high_threshold: float  # 高精力阈值
    low_threshold: float   # 低精力阈值
    optimal_sleep: float   # 最佳睡眠时长
    last_updated: datetime


@dataclass
class EnergyDigitalTwin:
    """用户精力数字孪生"""
    user_id: str

    # 当前状态
    current_energy: Optional[EnergyPrediction] = None
    real_time_score: float = 5.0

    # 预测曲线
    hourly_predictions: List[EnergyPrediction] = field(default_factory=list)
    daily_predictions: List[EnergyPrediction] = field(default_factory=list)

    # 精力模式
    patterns: List[EnergyPattern] = field(default_factory=list)

    # 个性化基线
    baseline: Optional[PersonalBaseline] = None

    # 统计数据
    stats: Dict[str, float] = field(default_factory=dict)

    # 建议
    recommendations: List[str] = field(default_factory=list)

    # 元数据
    last_updated: datetime = field(default_factory=datetime.utcnow)
    data_completeness: float = 0.0  # 数据完整度(0-1)


class DigitalTwinManager:
    """
    精力数字孪生管理器

    负责:
    1. 数据融合 - 整合多源数据
    2. 状态计算 - 实时精力评估
    3. 模式识别 - 发现精力规律
    4. 基线校准 - 个性化标准
    """

    def __init__(self):
        self.prediction_model: Optional[EnergyPredictionModel] = None
        logger.info("🔬 DigitalTwinManager initialized")

    async def initialize(self):
        """初始化"""
        self.prediction_model = await get_energy_prediction_model()
        logger.info("✅ DigitalTwinManager ready")

    async def get_digital_twin(
        self,
        user_id: str,
        db: AsyncSession,
        include_predictions: bool = True,
        prediction_hours: int = 24
    ) -> EnergyDigitalTwin:
        """
        获取用户的精力数字孪生

        Args:
            user_id: 用户ID
            db: 数据库会话
            include_predictions: 是否包含预测
            prediction_hours: 预测时长(小时)

        Returns:
            EnergyDigitalTwin: 用户精力数字孪生
        """
        logger.info(f"🔮 Building digital twin | User: {user_id[:8]}...")

        twin = EnergyDigitalTwin(user_id=user_id)

        # 1. 计算当前精力
        twin.current_energy = await self.prediction_model.predict_current_energy(
            user_id, db
        )
        twin.real_time_score = twin.current_energy.score

        # 2. 生成预测曲线
        if include_predictions:
            twin.hourly_predictions = await self.prediction_model.predict_future_energy(
                user_id, db, hours_ahead=prediction_hours
            )

            # 未来7天的每日预测（取每天10:00的预测值代表当天）
            daily_preds = []
            for day in range(7):
                future_time = datetime.utcnow() + timedelta(days=day)
                future_time = future_time.replace(hour=10, minute=0, second=0)

                # 计算该时间点的预测
                hour_diff = int((future_time - datetime.utcnow()).total_seconds() / 3600)
                if hour_diff < len(twin.hourly_predictions):
                    daily_preds.append(twin.hourly_predictions[hour_diff])

            twin.daily_predictions = daily_preds

        # 3. 识别精力模式
        twin.patterns = await self._identify_patterns(user_id, db)

        # 4. 计算个性化基线
        twin.baseline = await self._calculate_baseline(user_id, db)

        # 5. 统计数据
        twin.stats = await self._calculate_stats(user_id, db)

        # 6. 生成建议
        twin.recommendations = self._generate_twin_recommendations(twin)

        # 7. 计算数据完整度
        twin.data_completeness = await self._calculate_data_completeness(user_id, db)

        twin.last_updated = datetime.utcnow()

        logger.info(
            f"✅ Digital twin built | User: {user_id[:8]}... | "
            f"Current: {twin.real_time_score:.1f}/10 | "
            f"Patterns: {len(twin.patterns)} | "
            f"Completeness: {twin.data_completeness:.0%}"
        )

        return twin

    async def _identify_patterns(
        self,
        user_id: str,
        db: AsyncSession
    ) -> List[EnergyPattern]:
        """
        识别用户的精力模式

        模式类型:
        1. 日周期 (昼夜节律)
        2. 周周期 (工作日vs周末)
        3. 月周期 (女性月经周期)
        """
        patterns = []

        # 1. 识别日周期模式
        daily_pattern = await self._identify_daily_pattern(user_id, db)
        if daily_pattern:
            patterns.append(daily_pattern)

        # 2. 识别周周期模式
        weekly_pattern = await self._identify_weekly_pattern(user_id, db)
        if weekly_pattern:
            patterns.append(weekly_pattern)

        return patterns

    async def _identify_daily_pattern(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Optional[EnergyPattern]:
        """识别日周期模式 - 找出精力高峰和低谷时段"""
        # 查询过去30天的精力数据
        query = select(
            func.extract('hour', HealthData.recorded_at).label('hour'),
            func.avg(HealthData.value).label('avg_energy')
        ).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).group_by('hour').order_by('hour')

        result = await db.execute(query)
        hourly_avg = result.all()

        if len(hourly_avg) < 6:  # 数据不足
            return None

        # 分析高峰和低谷
        hourly_dict = {int(row.hour): row.avg_energy for row in hourly_avg}
        all_hours = list(hourly_dict.keys())
        all_energies = list(hourly_dict.values())

        if not all_energies:
            return None

        mean_energy = np.mean(all_energies)
        std_energy = np.std(all_energies)

        # 高精力时段 (高于平均值+0.5个标准差)
        peak_hours = [h for h in all_hours if hourly_dict[h] > mean_energy + 0.5 * std_energy]

        # 低精力时段 (低于平均值-0.5个标准差)
        low_hours = [h for h in all_hours if hourly_dict[h] < mean_energy - 0.5 * std_energy]

        # 生成描述
        if peak_hours:
            peak_range = f"{min(peak_hours)}:00-{max(peak_hours)}:00"
        else:
            peak_range = "暂无明显规律"

        description = f"你的精力高峰通常在 {peak_range}"

        return EnergyPattern(
            pattern_type="daily",
            description=description,
            peak_hours=sorted(peak_hours),
            low_hours=sorted(low_hours),
            confidence=min(1.0, len(hourly_avg) / 24)  # 数据覆盖度
        )

    async def _identify_weekly_pattern(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Optional[EnergyPattern]:
        """识别周周期模式 - 工作日vs周末差异"""
        # 查询过去8周的精力数据
        query = select(
            func.extract('dow', HealthData.recorded_at).label('day_of_week'),
            func.avg(HealthData.value).label('avg_energy')
        ).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(weeks=8)
            )
        ).group_by('day_of_week').order_by('day_of_week')

        result = await db.execute(query)
        weekly_avg = result.all()

        if len(weekly_avg) < 5:  # 数据不足
            return None

        # 分析工作日vs周末
        weekday_energy = []
        weekend_energy = []

        for row in weekly_avg:
            dow = int(row.day_of_week)  # 0=周日, 6=周六
            if dow in [0, 6]:  # 周末
                weekend_energy.append(row.avg_energy)
            else:  # 工作日
                weekday_energy.append(row.avg_energy)

        if not weekday_energy or not weekend_energy:
            return None

        avg_weekday = np.mean(weekday_energy)
        avg_weekend = np.mean(weekend_energy)

        # 生成描述
        if avg_weekend > avg_weekday + 0.5:
            description = f"周末精力明显高于工作日 ({avg_weekend:.1f} vs {avg_weekday:.1f})"
            peak_days = [0, 6]  # 周末
            low_days = [1, 2, 3, 4, 5]  # 工作日
        elif avg_weekday > avg_weekend + 0.5:
            description = f"工作日精力更高 ({avg_weekday:.1f} vs {avg_weekend:.1f})"
            peak_days = [1, 2, 3, 4, 5]
            low_days = [0, 6]
        else:
            description = "工作日和周末精力差异不大"
            peak_days = []
            low_days = []

        return EnergyPattern(
            pattern_type="weekly",
            description=description,
            peak_hours=peak_days,  # 这里用day_of_week代替hour
            low_hours=low_days,
            confidence=min(1.0, len(weekly_avg) / 7)
        )

    async def _calculate_baseline(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Optional[PersonalBaseline]:
        """
        计算个性化基线

        每个用户的"高精力"标准不同，需要建立个性化基线
        """
        # 查询过去30天的精力数据
        query = select(HealthData.value).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=30)
            )
        )

        result = await db.execute(query)
        energy_values = [row.value for row in result.all()]

        if len(energy_values) < 10:  # 数据不足
            return None

        # 计算统计量
        avg_energy = float(np.mean(energy_values))
        std_energy = float(np.std(energy_values))

        # 高精力阈值 (平均值 + 0.5个标准差)
        high_threshold = min(10.0, avg_energy + 0.5 * std_energy)

        # 低精力阈值 (平均值 - 0.5个标准差)
        low_threshold = max(1.0, avg_energy - 0.5 * std_energy)

        # 计算最佳睡眠时长 (基于睡眠数据和精力的相关性)
        optimal_sleep = await self._calculate_optimal_sleep(user_id, db)

        return PersonalBaseline(
            user_id=user_id,
            avg_energy=avg_energy,
            high_threshold=high_threshold,
            low_threshold=low_threshold,
            optimal_sleep=optimal_sleep,
            last_updated=datetime.utcnow()
        )

    async def _calculate_optimal_sleep(
        self,
        user_id: str,
        db: AsyncSession
    ) -> float:
        """计算用户的最佳睡眠时长"""
        # 查询睡眠和精力的配对数据
        query = select(
            HealthData.recorded_at,
            HealthData.data_type,
            HealthData.value
        ).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type.in_([
                    HealthDataType.SLEEP_DURATION,
                    HealthDataType.ENERGY_LEVEL
                ]),
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).order_by(HealthData.recorded_at)

        result = await db.execute(query)
        data = result.all()

        # 构建睡眠-精力对
        sleep_energy_pairs = []
        sleep_dict = {}
        energy_dict = {}

        for row in data:
            date_key = row.recorded_at.date()
            if row.data_type == HealthDataType.SLEEP_DURATION:
                sleep_dict[date_key] = row.value
            elif row.data_type == HealthDataType.ENERGY_LEVEL:
                if date_key not in energy_dict:
                    energy_dict[date_key] = []
                energy_dict[date_key].append(row.value)

        # 匹配睡眠和次日精力
        for date_key in sleep_dict:
            next_day = date_key + timedelta(days=1)
            if next_day in energy_dict:
                sleep = sleep_dict[date_key]
                avg_energy_next_day = np.mean(energy_dict[next_day])
                sleep_energy_pairs.append((sleep, avg_energy_next_day))

        if len(sleep_energy_pairs) < 5:
            return 8.0  # 默认8小时

        # 找出精力最高时对应的睡眠时长
        sorted_pairs = sorted(sleep_energy_pairs, key=lambda x: x[1], reverse=True)
        top_3_sleep = [pair[0] for pair in sorted_pairs[:3]]

        return float(np.mean(top_3_sleep))

    async def _calculate_stats(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, float]:
        """计算统计数据"""
        stats = {}

        # 过去7天平均精力
        query_7d = select(func.avg(HealthData.value)).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        result = await db.execute(query_7d)
        stats['avg_energy_7d'] = float(result.scalar() or 5.0)

        # 过去30天平均精力
        query_30d = select(func.avg(HealthData.value)).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=30)
            )
        )
        result = await db.execute(query_30d)
        stats['avg_energy_30d'] = float(result.scalar() or 5.0)

        # 过去7天平均睡眠
        query_sleep = select(func.avg(HealthData.value)).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.SLEEP_DURATION,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        result = await db.execute(query_sleep)
        stats['avg_sleep_7d'] = float(result.scalar() or 7.0)

        # 精力变异系数 (越小越稳定)
        query_std = select(func.stddev(HealthData.value)).where(
            and_(
                HealthData.user_id == user_id,
                HealthData.data_type == HealthDataType.ENERGY_LEVEL,
                HealthData.recorded_at >= datetime.utcnow() - timedelta(days=30)
            )
        )
        result = await db.execute(query_std)
        std = float(result.scalar() or 1.0)
        stats['energy_stability'] = 1.0 / (1.0 + std)  # 归一化到0-1

        return stats

    def _generate_twin_recommendations(
        self,
        twin: EnergyDigitalTwin
    ) -> List[str]:
        """基于数字孪生生成综合建议"""
        recommendations = []

        # 1. 基于当前精力的建议
        if twin.current_energy and twin.current_energy.recommendations:
            recommendations.extend(twin.current_energy.recommendations[:3])

        # 2. 基于精力模式的建议
        for pattern in twin.patterns:
            if pattern.pattern_type == "daily" and pattern.peak_hours:
                peak_time = f"{min(pattern.peak_hours)}:00-{max(pattern.peak_hours)}:00"
                recommendations.append(
                    f"📊 根据你的精力模式，{peak_time} 是处理重要任务的最佳时段"
                )

        # 3. 基于个性化基线的建议
        if twin.baseline and twin.current_energy:
            if twin.current_energy.score < twin.baseline.low_threshold:
                recommendations.append(
                    f"⚠️ 当前精力({twin.current_energy.score:.1f})低于你的个人基线({twin.baseline.avg_energy:.1f})，建议休息调整"
                )

            # 睡眠建议
            if twin.stats.get('avg_sleep_7d', 8) < twin.baseline.optimal_sleep - 0.5:
                recommendations.append(
                    f"💤 你的最佳睡眠时长是{twin.baseline.optimal_sleep:.1f}小时，最近平均只有{twin.stats.get('avg_sleep_7d', 0):.1f}小时"
                )

        # 4. 基于趋势的建议
        if twin.stats:
            avg_7d = twin.stats.get('avg_energy_7d', 5)
            avg_30d = twin.stats.get('avg_energy_30d', 5)

            if avg_7d < avg_30d - 1:
                recommendations.append(
                    f"📉 最近一周精力水平下降({avg_7d:.1f} vs 月均{avg_30d:.1f})，需要关注恢复"
                )
            elif avg_7d > avg_30d + 1:
                recommendations.append(
                    f"📈 最近一周精力提升明显({avg_7d:.1f} vs 月均{avg_30d:.1f})，保持这个节奏！"
                )

        return recommendations[:5]  # 最多5条建议

    async def _calculate_data_completeness(
        self,
        user_id: str,
        db: AsyncSession
    ) -> float:
        """计算数据完整度"""
        # 检查过去7天各类数据的可用性
        data_types = [
            HealthDataType.SLEEP_DURATION,
            HealthDataType.ENERGY_LEVEL,
            HealthDataType.STEPS,
            HealthDataType.HRV,
            HealthDataType.STRESS_LEVEL
        ]

        available_count = 0

        for data_type in data_types:
            query = select(func.count(HealthData.id)).where(
                and_(
                    HealthData.user_id == user_id,
                    HealthData.data_type == data_type,
                    HealthData.recorded_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
            result = await db.execute(query)
            count = result.scalar()

            if count > 0:
                available_count += 1

        return available_count / len(data_types)


# 全局单例
_digital_twin_manager: Optional[DigitalTwinManager] = None


async def get_digital_twin_manager() -> DigitalTwinManager:
    """获取数字孪生管理器单例"""
    global _digital_twin_manager

    if _digital_twin_manager is None:
        _digital_twin_manager = DigitalTwinManager()
        await _digital_twin_manager.initialize()

    return _digital_twin_manager
