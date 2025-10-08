"""
精力管理API路由
提供精力预测、数字孪生、精力模式分析等功能

基于核心竞争力文档:
- 精力预测模型 (Energy Prediction Model)
- 精力数字孪生 (Energy Digital Twin)
- 个性化基线 (Personal Baseline)
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_active_user
from app.ai.energy_prediction import (
    EnergyPredictionModel,
    get_energy_prediction_model,
    EnergyPrediction as EnergyPredictionResult,
    EnergyLevel
)
from app.ai.digital_twin import (
    DigitalTwinManager,
    get_digital_twin_manager,
    EnergyDigitalTwin,
    EnergyPattern as PatternResult,
    PersonalBaseline as BaselineResult
)
from pydantic import BaseModel, Field


# ============ Response Models ============

class EnergyPredictionResponse(BaseModel):
    """精力预测响应"""
    id: Optional[str] = None
    timestamp: datetime
    energy_level: str
    score: float
    confidence: float
    factors: dict
    recommendations: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-10-08T10:00:00Z",
                "energy_level": "high",
                "score": 7.8,
                "confidence": 0.85,
                "factors": {
                    "sleep": 2.0,
                    "physiology": 0.5,
                    "activity": 0.3,
                    "time_of_day": 1.5,
                    "subjective": 0.5
                },
                "recommendations": [
                    "精力充沛，建议优先处理重要任务",
                    "这是深度工作的好时机"
                ]
            }
        }


class PersonalBaselineResponse(BaseModel):
    """个性化基线响应"""
    user_id: str
    avg_energy: float
    high_threshold: float
    low_threshold: float
    optimal_sleep: float
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "avg_energy": 6.5,
                "high_threshold": 7.8,
                "low_threshold": 5.2,
                "optimal_sleep": 7.5,
                "last_updated": "2025-10-08T00:00:00Z"
            }
        }


class EnergyPatternResponse(BaseModel):
    """精力模式响应"""
    pattern_type: str
    description: str
    peak_hours: List[int]
    low_hours: List[int]
    confidence: float

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_type": "daily",
                "description": "你的精力高峰通常在 9:00-11:00",
                "peak_hours": [9, 10, 11],
                "low_hours": [14, 15],
                "confidence": 0.78
            }
        }


class DigitalTwinResponse(BaseModel):
    """数字孪生响应"""
    user_id: str
    current_energy: EnergyPredictionResponse
    hourly_predictions: List[EnergyPredictionResponse]
    daily_predictions: List[EnergyPredictionResponse]
    patterns: List[EnergyPatternResponse]
    baseline: Optional[PersonalBaselineResponse]
    stats: dict
    recommendations: List[str]
    data_completeness: float
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "current_energy": {},
                "hourly_predictions": [],
                "daily_predictions": [],
                "patterns": [],
                "baseline": None,
                "stats": {
                    "avg_energy_7d": 6.5,
                    "avg_energy_30d": 6.3,
                    "avg_sleep_7d": 7.2,
                    "energy_stability": 0.85
                },
                "recommendations": [],
                "data_completeness": 0.75,
                "last_updated": "2025-10-08T10:00:00Z"
            }
        }


# ============ Router ============

router = APIRouter(
    prefix="/energy",
    tags=["Energy Management"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"}
    }
)


@router.get(
    "/current",
    response_model=EnergyPredictionResponse,
    summary="获取当前精力状态",
    description="预测用户当前的精力水平，包括分数、等级、影响因素和建议"
)
async def get_current_energy(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前精力状态

    基于以下因素综合评估:
    - 睡眠数据 (时长、质量)
    - 生理指标 (HRV、心率)
    - 活动数据 (步数、运动)
    - 时间因素 (昼夜节律)
    - 主观感受 (压力、情绪)
    """
    try:
        prediction_model = await get_energy_prediction_model()

        # 预测当前精力
        prediction = await prediction_model.predict_current_energy(
            str(current_user.id),
            db
        )

        return EnergyPredictionResponse(
            id=prediction.id,
            timestamp=prediction.timestamp,
            energy_level=prediction.energy_level.value,
            score=prediction.score,
            confidence=prediction.confidence,
            factors=prediction.factors,
            recommendations=prediction.recommendations
        )

    except Exception as e:
        logger.error(f"Failed to get current energy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict energy: {str(e)}"
        )


@router.get(
    "/predict",
    response_model=List[EnergyPredictionResponse],
    summary="预测未来精力曲线",
    description="预测未来24小时的精力变化曲线"
)
async def predict_future_energy(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    预测未来精力曲线

    Args:
        hours: 预测时长(小时)，默认24小时

    Returns:
        未来各时间点的精力预测列表
    """
    if hours < 1 or hours > 168:  # 最多预测7天
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours must be between 1 and 168"
        )

    try:
        prediction_model = await get_energy_prediction_model()

        # 预测未来精力
        predictions = await prediction_model.predict_future_energy(
            str(current_user.id),
            db,
            hours_ahead=hours
        )

        return [
            EnergyPredictionResponse(
                timestamp=p.timestamp,
                energy_level=p.energy_level.value,
                score=p.score,
                confidence=p.confidence,
                factors=p.factors,
                recommendations=p.recommendations
            )
            for p in predictions
        ]

    except Exception as e:
        logger.error(f"Failed to predict future energy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict future energy: {str(e)}"
        )


@router.get(
    "/digital-twin",
    response_model=DigitalTwinResponse,
    summary="获取精力数字孪生",
    description="获取用户的完整精力数字孪生，包括当前状态、预测曲线、精力模式、个性化基线等"
)
async def get_digital_twin(
    include_predictions: bool = True,
    prediction_hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取精力数字孪生

    这是核心竞争力的基础 - 为每个用户构建动态的精力数字模型

    包含:
    - 当前精力状态
    - 未来精力预测曲线
    - 个人精力模式 (日周期、周周期)
    - 个性化基线校准
    - 统计数据和建议
    """
    try:
        twin_manager = await get_digital_twin_manager()

        # 获取数字孪生
        twin = await twin_manager.get_digital_twin(
            str(current_user.id),
            db,
            include_predictions=include_predictions,
            prediction_hours=prediction_hours
        )

        # 转换为响应模型
        response = DigitalTwinResponse(
            user_id=twin.user_id,
            current_energy=EnergyPredictionResponse(
                timestamp=twin.current_energy.timestamp,
                energy_level=twin.current_energy.energy_level.value,
                score=twin.current_energy.score,
                confidence=twin.current_energy.confidence,
                factors=twin.current_energy.factors,
                recommendations=twin.current_energy.recommendations
            ) if twin.current_energy else None,
            hourly_predictions=[
                EnergyPredictionResponse(
                    timestamp=p.timestamp,
                    energy_level=p.energy_level.value,
                    score=p.score,
                    confidence=p.confidence,
                    factors=p.factors,
                    recommendations=[]
                )
                for p in twin.hourly_predictions
            ],
            daily_predictions=[
                EnergyPredictionResponse(
                    timestamp=p.timestamp,
                    energy_level=p.energy_level.value,
                    score=p.score,
                    confidence=p.confidence,
                    factors=p.factors,
                    recommendations=[]
                )
                for p in twin.daily_predictions
            ],
            patterns=[
                EnergyPatternResponse(
                    pattern_type=p.pattern_type,
                    description=p.description,
                    peak_hours=p.peak_hours,
                    low_hours=p.low_hours,
                    confidence=p.confidence
                )
                for p in twin.patterns
            ],
            baseline=PersonalBaselineResponse(
                user_id=twin.baseline.user_id,
                avg_energy=twin.baseline.avg_energy,
                high_threshold=twin.baseline.high_threshold,
                low_threshold=twin.baseline.low_threshold,
                optimal_sleep=twin.baseline.optimal_sleep,
                last_updated=twin.baseline.last_updated
            ) if twin.baseline else None,
            stats=twin.stats,
            recommendations=twin.recommendations,
            data_completeness=twin.data_completeness,
            last_updated=twin.last_updated
        )

        logger.info(
            f"✅ Digital twin retrieved | User: {current_user.id} | "
            f"Energy: {twin.real_time_score:.1f}/10 | "
            f"Patterns: {len(twin.patterns)} | "
            f"Completeness: {twin.data_completeness:.0%}"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to get digital twin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get digital twin: {str(e)}"
        )


@router.get(
    "/patterns",
    response_model=List[EnergyPatternResponse],
    summary="获取精力模式",
    description="识别用户的精力模式，包括日周期和周周期规律"
)
async def get_energy_patterns(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取精力模式

    识别:
    - 日周期模式 (哪些时段精力最好)
    - 周周期模式 (工作日vs周末差异)
    """
    try:
        twin_manager = await get_digital_twin_manager()

        # 获取模式
        patterns = await twin_manager._identify_patterns(
            str(current_user.id),
            db
        )

        return [
            EnergyPatternResponse(
                pattern_type=p.pattern_type,
                description=p.description,
                peak_hours=p.peak_hours,
                low_hours=p.low_hours,
                confidence=p.confidence
            )
            for p in patterns
        ]

    except Exception as e:
        logger.error(f"Failed to get energy patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get energy patterns: {str(e)}"
        )


@router.get(
    "/baseline",
    response_model=PersonalBaselineResponse,
    summary="获取个性化基线",
    description="获取用户的个性化精力基线，包括平均精力、高低阈值、最佳睡眠时长等"
)
async def get_personal_baseline(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取个性化基线

    每个用户的"高精力"标准不同，基线提供:
    - 个人平均精力水平
    - 高精力阈值
    - 低精力阈值
    - 最佳睡眠时长
    """
    try:
        twin_manager = await get_digital_twin_manager()

        # 计算基线
        baseline = await twin_manager._calculate_baseline(
            str(current_user.id),
            db
        )

        if not baseline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insufficient data to calculate baseline (need at least 10 energy records)"
            )

        return PersonalBaselineResponse(
            user_id=baseline.user_id,
            avg_energy=baseline.avg_energy,
            high_threshold=baseline.high_threshold,
            low_threshold=baseline.low_threshold,
            optimal_sleep=baseline.optimal_sleep,
            last_updated=baseline.last_updated
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get baseline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=dict,
    summary="获取精力统计数据",
    description="获取用户的精力统计数据，包括7天/30天平均精力、睡眠、稳定性等"
)
async def get_energy_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取精力统计数据

    包含:
    - 过去7天平均精力
    - 过去30天平均精力
    - 过去7天平均睡眠
    - 精力稳定性指数
    """
    try:
        twin_manager = await get_digital_twin_manager()

        stats = await twin_manager._calculate_stats(
            str(current_user.id),
            db
        )

        return stats

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


# ============ Prediction Validation ============

class ValidatePredictionRequest(BaseModel):
    """验证预测请求"""
    prediction_id: str = Field(..., description="预测记录ID")
    actual_energy: float = Field(..., ge=1, le=10, description="实际精力(1-10)")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "actual_energy": 7.5
            }
        }


class ValidationResponse(BaseModel):
    """验证响应"""
    prediction_id: str
    predicted_energy: float
    actual_energy: float
    prediction_error: float
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "predicted_energy": 7.0,
                "actual_energy": 7.5,
                "prediction_error": 0.5,
                "message": "预测误差: 0.5分，模型表现良好"
            }
        }


class ModelAccuracyResponse(BaseModel):
    """模型准确性统计响应"""
    total_predictions: int
    validated_predictions: int
    validation_rate: float
    mean_absolute_error: float
    root_mean_square_error: float
    accuracy_within_1: float
    accuracy_within_2: float
    period_days: int

    class Config:
        json_schema_extra = {
            "example": {
                "total_predictions": 100,
                "validated_predictions": 85,
                "validation_rate": 0.85,
                "mean_absolute_error": 1.2,
                "root_mean_square_error": 1.5,
                "accuracy_within_1": 0.65,
                "accuracy_within_2": 0.90,
                "period_days": 30
            }
        }


@router.post(
    "/validate-prediction",
    response_model=ValidationResponse,
    summary="验证精力预测",
    description="用户提交实际精力值，用于验证预测准确性并优化模型"
)
async def validate_prediction(
    request: ValidatePredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    验证精力预测

    用户在预测时间点后提交实际精力值，系统计算预测误差并存储用于模型优化
    """
    try:
        from app.models.energy import EnergyPrediction as EnergyPredictionModel
        from sqlalchemy import select, update

        # 查找预测记录
        query = select(EnergyPredictionModel).where(
            EnergyPredictionModel.id == UUID(request.prediction_id),
            EnergyPredictionModel.user_id == current_user.id
        )

        result = await db.execute(query)
        prediction = result.scalar_one_or_none()

        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found"
            )

        # 计算预测误差
        prediction_error = abs(request.actual_energy - prediction.energy_score)

        # 更新预测记录
        update_stmt = update(EnergyPredictionModel).where(
            EnergyPredictionModel.id == UUID(request.prediction_id)
        ).values(
            actual_energy=request.actual_energy,
            prediction_error=prediction_error
        )

        await db.execute(update_stmt)
        await db.commit()

        # 生成反馈消息
        if prediction_error < 1:
            message = f"预测误差: {prediction_error:.1f}分，模型表现优秀！"
        elif prediction_error < 2:
            message = f"预测误差: {prediction_error:.1f}分，模型表现良好"
        else:
            message = f"预测误差: {prediction_error:.1f}分，我们会继续优化模型"

        logger.info(
            f"✅ Prediction validated | User: {current_user.id} | "
            f"Predicted: {prediction.energy_score:.1f} | "
            f"Actual: {request.actual_energy:.1f} | "
            f"Error: {prediction_error:.1f}"
        )

        return ValidationResponse(
            prediction_id=str(prediction.id),
            predicted_energy=prediction.energy_score,
            actual_energy=request.actual_energy,
            prediction_error=prediction_error,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate prediction: {str(e)}"
        )


@router.get(
    "/model-accuracy",
    response_model=ModelAccuracyResponse,
    summary="获取模型准确性统计",
    description="获取预测模型的准确性指标，包括MAE、RMSE等"
)
async def get_model_accuracy(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取模型准确性统计

    Args:
        days: 统计周期(天)，默认30天

    Returns:
        模型准确性指标
    """
    try:
        from app.models.energy import EnergyPrediction as EnergyPredictionModel
        from sqlalchemy import select, func, and_
        from datetime import datetime, timedelta
        import numpy as np

        # 查询已验证的预测记录
        query = select(EnergyPredictionModel).where(
            and_(
                EnergyPredictionModel.user_id == current_user.id,
                EnergyPredictionModel.actual_energy.isnot(None),
                EnergyPredictionModel.predicted_at >= datetime.utcnow() - timedelta(days=days)
            )
        )

        result = await db.execute(query)
        validated_predictions = result.scalars().all()

        # 统计总预测数
        total_query = select(func.count(EnergyPredictionModel.id)).where(
            and_(
                EnergyPredictionModel.user_id == current_user.id,
                EnergyPredictionModel.predicted_at >= datetime.utcnow() - timedelta(days=days)
            )
        )
        total_result = await db.execute(total_query)
        total_predictions = total_result.scalar() or 0

        if len(validated_predictions) == 0:
            return ModelAccuracyResponse(
                total_predictions=total_predictions,
                validated_predictions=0,
                validation_rate=0.0,
                mean_absolute_error=0.0,
                root_mean_square_error=0.0,
                accuracy_within_1=0.0,
                accuracy_within_2=0.0,
                period_days=days
            )

        # 计算误差指标
        errors = [p.prediction_error for p in validated_predictions]
        mae = float(np.mean(errors))
        rmse = float(np.sqrt(np.mean([e**2 for e in errors])))

        # 计算准确率
        within_1 = sum(1 for e in errors if e <= 1.0) / len(errors)
        within_2 = sum(1 for e in errors if e <= 2.0) / len(errors)

        validation_rate = len(validated_predictions) / total_predictions if total_predictions > 0 else 0

        logger.info(
            f"📊 Model accuracy | User: {current_user.id} | "
            f"Validated: {len(validated_predictions)}/{total_predictions} | "
            f"MAE: {mae:.2f} | RMSE: {rmse:.2f}"
        )

        return ModelAccuracyResponse(
            total_predictions=total_predictions,
            validated_predictions=len(validated_predictions),
            validation_rate=validation_rate,
            mean_absolute_error=mae,
            root_mean_square_error=rmse,
            accuracy_within_1=within_1,
            accuracy_within_2=within_2,
            period_days=days
        )

    except Exception as e:
        logger.error(f"Failed to get model accuracy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model accuracy: {str(e)}"
        )
