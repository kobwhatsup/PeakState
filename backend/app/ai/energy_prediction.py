"""
精力预测模型 (Energy Prediction Model)
基于用户历史数据预测未来精力状态

MVP阶段: 使用基于规则的启发式模型
后续升级: Random Forest -> XGBoost -> LSTM
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from loguru import logger

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.health_data import HealthData, HealthDataType


class EnergyLevel(str, Enum):
    """精力水平枚举"""
    HIGH = "high"       # 高精力 (7-10分)
    MEDIUM = "medium"   # 中等精力 (4-6分)
    LOW = "low"         # 低精力 (1-3分)


@dataclass
class EnergyPrediction:
    """精力预测结果"""
    timestamp: datetime
    energy_level: EnergyLevel
    score: float  # 1-10分
    confidence: float  # 0-1
    factors: Dict[str, float]  # 影响因素权重
    recommendations: List[str]  # 建议
    id: Optional[str] = None  # 预测记录ID(保存到数据库后填充)


@dataclass
class HealthFeatures:
    """健康特征集"""
    # 睡眠特征
    sleep_duration: float = 0.0  # 睡眠时长(小时)
    sleep_quality: float = 0.0   # 睡眠质量(1-100)
    sleep_debt: float = 0.0      # 睡眠负债(小时)

    # 生理特征
    hrv: float = 0.0             # 心率变异性
    resting_heart_rate: float = 0.0  # 静息心率

    # 活动特征
    steps: int = 0               # 步数
    exercise_minutes: int = 0    # 运动时长(分钟)
    active_energy: float = 0.0   # 活动能量(kcal)

    # 主观特征
    subjective_energy: float = 0.0  # 主观精力评分(1-10)
    stress_level: float = 0.0    # 压力水平(1-100)
    mood: float = 0.0            # 心情(1-10)

    # 时间特征
    hour_of_day: int = 0         # 小时(0-23)
    day_of_week: int = 0         # 星期(0-6, 0=周一)
    is_weekend: bool = False     # 是否周末

    # 历史特征
    avg_energy_7d: float = 0.0   # 过去7天平均精力
    avg_energy_30d: float = 0.0  # 过去30天平均精力

    # 环境特征
    temperature: float = 0.0     # 温度(°C)
    humidity: int = 0            # 湿度(%)
    air_quality: int = 0         # 空气质量指数
    weather: str = ""            # 天气状况


class EnergyPredictionModel:
    """
    精力预测模型

    MVP阶段实现:
    - 基于规则的启发式算法
    - 快速上线，验证产品价值

    V2.0升级计划:
    - Random Forest/XGBoost
    - 基于用户历史数据训练

    V3.0升级计划:
    - LSTM时间序列预测
    - 个性化联邦学习
    """

    def __init__(self):
        self.model_version = "1.0.0-heuristic"
        logger.info(f"🔮 EnergyPredictionModel initialized | Version: {self.model_version}")

    async def predict_current_energy(
        self,
        user_id: str,
        db: AsyncSession,
        save_to_db: bool = True
    ) -> EnergyPrediction:
        """
        预测当前精力状态

        Args:
            user_id: 用户ID
            db: 数据库会话
            save_to_db: 是否保存预测结果到数据库

        Returns:
            EnergyPrediction: 当前精力预测
        """
        # 1. 提取特征
        features = await self._extract_features(user_id, db, datetime.utcnow())

        # 2. 计算精力分数
        score, factors = self._calculate_energy_score(features)

        # 3. 判断精力等级
        energy_level = self._classify_energy_level(score)

        # 4. 生成建议
        recommendations = self._generate_recommendations(score, energy_level, features)

        # 5. 计算置信度
        confidence = self._calculate_confidence(features)

        current_time = datetime.utcnow()

        prediction = EnergyPrediction(
            timestamp=current_time,
            energy_level=energy_level,
            score=score,
            confidence=confidence,
            factors=factors,
            recommendations=recommendations
        )

        # 6. 保存到数据库(可选)
        if save_to_db:
            prediction_id = await self._save_prediction(
                user_id=user_id,
                db=db,
                prediction=prediction,
                target_time=current_time
            )
            # 在prediction对象中添加ID属性(用于前端)
            prediction.id = prediction_id

        logger.info(
            f"⚡️ Current energy predicted | User: {user_id[:8]}... | "
            f"Level: {energy_level.value} | Score: {score:.1f}/10"
        )

        return prediction

    async def predict_future_energy(
        self,
        user_id: str,
        db: AsyncSession,
        hours_ahead: int = 24
    ) -> List[EnergyPrediction]:
        """
        预测未来精力曲线

        Args:
            user_id: 用户ID
            db: 数据库会话
            hours_ahead: 预测未来N小时

        Returns:
            List[EnergyPrediction]: 未来各时间点精力预测
        """
        predictions = []
        current_time = datetime.utcnow()

        for hour in range(hours_ahead):
            future_time = current_time + timedelta(hours=hour)

            # 提取该时间点的特征
            features = await self._extract_features(user_id, db, future_time)

            # 预测精力
            score, factors = self._calculate_energy_score(features, is_future=True)
            energy_level = self._classify_energy_level(score)
            confidence = self._calculate_confidence(features, is_future=True)

            predictions.append(EnergyPrediction(
                timestamp=future_time,
                energy_level=energy_level,
                score=score,
                confidence=confidence,
                factors=factors,
                recommendations=[]
            ))

        logger.info(
            f"📈 Future energy predicted | User: {user_id[:8]}... | "
            f"Hours: {hours_ahead} | Avg score: {np.mean([p.score for p in predictions]):.1f}"
        )

        return predictions

    async def _extract_features(
        self,
        user_id: str,
        db: AsyncSession,
        target_time: datetime
    ) -> HealthFeatures:
        """提取健康特征"""
        features = HealthFeatures()

        # 时间特征
        features.hour_of_day = target_time.hour
        features.day_of_week = target_time.weekday()
        features.is_weekend = target_time.weekday() >= 5

        # 查询最近的健康数据
        query = select(HealthData).where(
            HealthData.user_id == user_id,
            HealthData.recorded_at >= target_time - timedelta(days=1),
            HealthData.recorded_at <= target_time
        ).order_by(HealthData.recorded_at.desc())

        result = await db.execute(query)
        health_data_list = result.scalars().all()

        # 提取各类特征
        for data in health_data_list:
            if data.data_type == HealthDataType.SLEEP_DURATION:
                features.sleep_duration = data.value
            elif data.data_type == HealthDataType.SLEEP_QUALITY:
                features.sleep_quality = data.value
            elif data.data_type == HealthDataType.HRV:
                features.hrv = data.value
            elif data.data_type == HealthDataType.HEART_RATE_RESTING:
                features.resting_heart_rate = data.value
            elif data.data_type == HealthDataType.STEPS:
                features.steps = int(data.value)
            elif data.data_type == HealthDataType.EXERCISE_MINUTES:
                features.exercise_minutes = int(data.value)
            elif data.data_type == HealthDataType.ACTIVE_ENERGY:
                features.active_energy = data.value
            elif data.data_type == HealthDataType.ENERGY_LEVEL:
                features.subjective_energy = data.value
            elif data.data_type == HealthDataType.STRESS_LEVEL:
                features.stress_level = data.value
            elif data.data_type == HealthDataType.MOOD:
                features.mood = data.value

        # 计算睡眠负债 (理想睡眠8小时)
        features.sleep_debt = max(0, 8.0 - features.sleep_duration)

        # 计算历史平均精力
        features.avg_energy_7d = await self._get_avg_energy(user_id, db, days=7)
        features.avg_energy_30d = await self._get_avg_energy(user_id, db, days=30)

        # 提取环境数据
        from app.models.energy import EnvironmentData
        env_query = select(EnvironmentData).where(
            EnvironmentData.user_id == user_id,
            EnvironmentData.recorded_at <= target_time
        ).order_by(EnvironmentData.recorded_at.desc()).limit(1)

        env_result = await db.execute(env_query)
        env_data = env_result.scalar_one_or_none()

        if env_data:
            features.temperature = env_data.temperature or 0.0
            features.humidity = env_data.humidity or 0
            features.air_quality = env_data.air_quality or 0
            features.weather = env_data.weather or ""

        return features

    async def _get_avg_energy(
        self,
        user_id: str,
        db: AsyncSession,
        days: int
    ) -> float:
        """获取过去N天的平均精力"""
        query = select(func.avg(HealthData.value)).where(
            HealthData.user_id == user_id,
            HealthData.data_type == HealthDataType.ENERGY_LEVEL,
            HealthData.recorded_at >= datetime.utcnow() - timedelta(days=days)
        )

        result = await db.execute(query)
        avg = result.scalar()

        return float(avg) if avg else 5.0  # 默认中等精力

    def _calculate_energy_score(
        self,
        features: HealthFeatures,
        is_future: bool = False
    ) -> Tuple[float, Dict[str, float]]:
        """
        计算精力分数（1-10分）

        基于规则的评分算法:
        1. 基础分数: 5分
        2. 睡眠因素: ±3分
        3. 生理因素: ±1分
        4. 活动因素: ±1分
        5. 时间因素: ±2分
        6. 主观因素: ±1分
        """
        base_score = 5.0
        factors = {}

        # 1. 睡眠因素 (权重最大: ±3分)
        sleep_score = 0.0
        if features.sleep_duration > 0:
            # 理想睡眠7-9小时
            if 7 <= features.sleep_duration <= 9:
                sleep_score = 2.0
            elif 6 <= features.sleep_duration < 7 or 9 < features.sleep_duration <= 10:
                sleep_score = 1.0
            elif features.sleep_duration < 6:
                sleep_score = -2.0 - (6 - features.sleep_duration) * 0.5
            else:  # >10小时
                sleep_score = -1.0

            # 睡眠质量加成
            if features.sleep_quality > 0:
                quality_bonus = (features.sleep_quality - 50) / 50  # -1到+1
                sleep_score += quality_bonus

        sleep_score = max(-3, min(3, sleep_score))
        factors['sleep'] = sleep_score

        # 2. 生理因素 (±1分)
        physio_score = 0.0
        if features.hrv > 0:
            # HRV越高越好 (假设正常范围20-100ms)
            hrv_normalized = (features.hrv - 60) / 40  # -1到+1
            physio_score += hrv_normalized * 0.5

        if features.resting_heart_rate > 0:
            # 静息心率越低越好 (正常范围50-100)
            hr_normalized = (75 - features.resting_heart_rate) / 25
            physio_score += hr_normalized * 0.5

        physio_score = max(-1, min(1, physio_score))
        factors['physiology'] = physio_score

        # 3. 活动因素 (±1分)
        activity_score = 0.0
        if features.exercise_minutes > 0:
            # 适度运动是好的
            if 20 <= features.exercise_minutes <= 60:
                activity_score = 0.5
            elif features.exercise_minutes > 60:
                # 过度运动可能疲劳
                activity_score = 0.5 - (features.exercise_minutes - 60) / 120

        if features.steps > 0:
            # 步数目标8000-12000
            if 8000 <= features.steps <= 12000:
                activity_score += 0.5
            elif features.steps < 8000:
                activity_score += (features.steps / 8000) * 0.3

        activity_score = max(-1, min(1, activity_score))
        factors['activity'] = activity_score

        # 4. 时间因素 (±2分) - 自然昼夜节律
        time_score = 0.0
        hour = features.hour_of_day

        if 6 <= hour <= 11:  # 早晨精力上升
            time_score = 1.5
        elif 12 <= hour <= 14:  # 午后微降
            time_score = 0.5
        elif 15 <= hour <= 18:  # 下午恢复
            time_score = 1.0
        elif 19 <= hour <= 22:  # 晚上下降
            time_score = -0.5
        else:  # 深夜/凌晨
            time_score = -2.0

        # 周末精力可能更高
        if features.is_weekend:
            time_score += 0.5

        time_score = max(-2, min(2, time_score))
        factors['time_of_day'] = time_score

        # 5. 主观因素 (±1分)
        subjective_score = 0.0
        if features.subjective_energy > 0:
            # 将1-10的主观评分转换为-1到+1
            subjective_score = (features.subjective_energy - 5.5) / 4.5

        if features.stress_level > 0:
            # 压力越高，精力越低
            stress_impact = -(features.stress_level - 50) / 50 * 0.5
            subjective_score += stress_impact

        subjective_score = max(-1, min(1, subjective_score))
        factors['subjective'] = subjective_score

        # 6. 历史趋势 (±0.5分)
        trend_score = 0.0
        if features.avg_energy_7d > 0:
            # 相对于历史平均的偏差
            trend_score = (features.avg_energy_7d - 5) / 10

        trend_score = max(-0.5, min(0.5, trend_score))
        factors['trend'] = trend_score

        # 7. 环境因素 (±1分)
        environment_score = 0.0

        # 温度影响 (舒适温度18-25°C)
        if features.temperature > 0:
            if 18 <= features.temperature <= 25:
                environment_score += 0.3
            elif features.temperature < 10 or features.temperature > 32:
                environment_score -= 0.3
            elif features.temperature < 18 or features.temperature > 25:
                environment_score -= 0.1

        # 湿度影响 (舒适湿度40-70%)
        if features.humidity > 0:
            if 40 <= features.humidity <= 70:
                environment_score += 0.2
            elif features.humidity < 30 or features.humidity > 80:
                environment_score -= 0.2

        # 空气质量影响 (AQI < 50优秀, >150不健康)
        if features.air_quality > 0:
            if features.air_quality < 50:
                environment_score += 0.3
            elif features.air_quality > 150:
                environment_score -= 0.4
            elif features.air_quality > 100:
                environment_score -= 0.2

        # 天气状况影响
        if features.weather:
            weather_lower = features.weather.lower()
            if any(w in weather_lower for w in ['晴', 'clear', 'sunny']):
                environment_score += 0.2
            elif any(w in weather_lower for w in ['雨', 'rain', 'storm']):
                environment_score -= 0.1

        environment_score = max(-1, min(1, environment_score))
        factors['environment'] = environment_score

        # 计算最终分数
        total_score = base_score + sum(factors.values())

        # 限制在1-10范围
        total_score = max(1, min(10, total_score))

        return total_score, factors

    def _classify_energy_level(self, score: float) -> EnergyLevel:
        """将分数分类为精力等级"""
        if score >= 7:
            return EnergyLevel.HIGH
        elif score >= 4:
            return EnergyLevel.MEDIUM
        else:
            return EnergyLevel.LOW

    def _generate_recommendations(
        self,
        score: float,
        energy_level: EnergyLevel,
        features: HealthFeatures
    ) -> List[str]:
        """生成个性化建议"""
        recommendations = []

        # 睡眠建议
        if features.sleep_duration < 7:
            recommendations.append(
                f"💤 昨晚只睡了{features.sleep_duration:.1f}小时，今晚尽量早点休息"
            )

        # 精力低时的快速充电建议
        if energy_level == EnergyLevel.LOW:
            recommendations.append("⚡️ 精力较低，建议:")
            recommendations.append("  - 做5分钟深呼吸练习")
            recommendations.append("  - 用冷水洗把脸")
            recommendations.append("  - 短暂走动10分钟")

        # 精力高时的利用建议
        elif energy_level == EnergyLevel.HIGH:
            recommendations.append("🎯 精力充沛，建议:")
            recommendations.append("  - 优先处理重要且复杂的任务")
            recommendations.append("  - 这是深度工作的好时机")

        # 运动建议
        if features.exercise_minutes == 0:
            recommendations.append("🏃 今天还没运动，建议20-30分钟轻度活动")

        # 压力管理
        if features.stress_level > 70:
            recommendations.append("🧘 压力较高，建议做10分钟正念冥想")

        return recommendations

    def _calculate_confidence(
        self,
        features: HealthFeatures,
        is_future: bool = False
    ) -> float:
        """
        计算预测置信度

        置信度取决于:
        1. 数据完整性 (有多少特征可用)
        2. 历史数据量 (用户使用时长)
        3. 是否未来预测 (未来预测置信度降低)
        """
        confidence = 0.5  # 基础置信度

        # 数据完整性
        available_features = 0
        total_features = 10

        if features.sleep_duration > 0:
            available_features += 1
        if features.sleep_quality > 0:
            available_features += 1
        if features.hrv > 0:
            available_features += 1
        if features.subjective_energy > 0:
            available_features += 2  # 主观数据权重更高
        if features.exercise_minutes > 0:
            available_features += 1
        if features.avg_energy_7d > 0:
            available_features += 2  # 历史数据权重更高
        if features.stress_level > 0:
            available_features += 1
        if features.mood > 0:
            available_features += 1

        data_completeness = available_features / total_features
        confidence += data_completeness * 0.3

        # 历史数据加成
        if features.avg_energy_30d > 0:
            confidence += 0.1

        # 未来预测降低置信度
        if is_future:
            confidence *= 0.8

        return min(1.0, confidence)

    async def _save_prediction(
        self,
        user_id: str,
        db: AsyncSession,
        prediction: EnergyPrediction,
        target_time: datetime
    ) -> str:
        """
        保存预测结果到数据库

        Args:
            user_id: 用户ID
            db: 数据库会话
            prediction: 预测结果
            target_time: 预测目标时间

        Returns:
            str: 预测记录ID
        """
        from app.models.energy import EnergyPrediction as EnergyPredictionModel
        import uuid

        # 创建数据库记录
        prediction_record = EnergyPredictionModel(
            user_id=uuid.UUID(user_id),
            predicted_at=prediction.timestamp,
            target_time=target_time,
            energy_level=prediction.energy_level.value,
            energy_score=prediction.score,
            confidence=prediction.confidence,
            factors=prediction.factors,
            recommendations=prediction.recommendations,
            model_version=self.model_version
        )

        db.add(prediction_record)
        await db.commit()
        await db.refresh(prediction_record)

        logger.debug(
            f"💾 Prediction saved | ID: {prediction_record.id} | "
            f"Score: {prediction.score:.1f}"
        )

        return str(prediction_record.id)


# 全局单例
_energy_prediction_model: Optional[EnergyPredictionModel] = None


async def get_energy_prediction_model() -> EnergyPredictionModel:
    """获取精力预测模型单例"""
    global _energy_prediction_model

    if _energy_prediction_model is None:
        _energy_prediction_model = EnergyPredictionModel()

    return _energy_prediction_model
