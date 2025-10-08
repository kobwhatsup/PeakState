"""
健康数据API端点
提供健康数据的录入、查询、统计功能
"""

from datetime import datetime
from typing import List, Optional, Annotated
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DatabaseSession
from app.crud import health_data as health_crud
from app.models.health_data import HealthData, HealthDataType, HealthDataSource
from app.schemas.health import (
    HealthDataCreate,
    HealthDataResponse,
    HealthDataBatchCreate,
    HealthSummaryResponse,
    HealthDataListResponse,
    HealthSyncRequest,
    HealthSyncResponse
)


router = APIRouter(prefix="/health", tags=["健康数据"])


@router.post("/data", response_model=HealthDataResponse, status_code=status.HTTP_201_CREATED)
async def create_health_data(
    data: HealthDataCreate,
    db: DatabaseSession,
    current_user: CurrentUser
) -> HealthDataResponse:
    """
    创建单条健康数据

    Args:
        data: 健康数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的健康数据
    """
    # 检查数据类型是否有效
    valid_types = [attr for attr in dir(HealthDataType) if not attr.startswith("_")]
    if data.data_type not in [getattr(HealthDataType, t) for t in valid_types]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data type: {data.data_type}"
        )

    # 如果有external_id,检查是否重复
    if data.external_id:
        is_duplicate = await health_crud.check_duplicate_sync(
            db, current_user.id, data.external_id
        )
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Data already synced"
            )

    health_data = await health_crud.create_health_data(
        db=db,
        user_id=current_user.id,
        data_type=data.data_type,
        value=data.value,
        source=data.source or HealthDataSource.MANUAL,
        unit=data.unit,
        recorded_at=data.recorded_at,
        extra_data=data.extra_data,
        external_id=data.external_id
    )

    return HealthDataResponse.model_validate(health_data)


@router.post("/data/batch", response_model=List[HealthDataResponse], status_code=status.HTTP_201_CREATED)
async def create_health_data_batch(
    batch_data: HealthDataBatchCreate,
    db: DatabaseSession,
    current_user: CurrentUser
) -> List[HealthDataResponse]:
    """
    批量创建健康数据

    Args:
        batch_data: 批量健康数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        创建的健康数据列表
    """
    health_data_list = []

    for data in batch_data.data:
        # 跳过重复数据
        if data.external_id:
            is_duplicate = await health_crud.check_duplicate_sync(
                db, current_user.id, data.external_id
            )
            if is_duplicate:
                continue

        health_data_obj = HealthData(
            user_id=current_user.id,
            data_type=data.data_type,
            value=data.value,
            source=data.source or HealthDataSource.MANUAL,
            unit=data.unit,
            recorded_at=data.recorded_at or datetime.utcnow(),
            extra_data=data.extra_data,
            external_id=data.external_id,
            synced_at=datetime.utcnow()
        )
        health_data_list.append(health_data_obj)

    if not health_data_list:
        return []

    created_data = await health_crud.create_health_data_batch(db, health_data_list)

    return [HealthDataResponse.model_validate(d) for d in created_data]


@router.get("/data/{data_type}", response_model=HealthDataListResponse)
async def get_health_data_by_type(
    data_type: str,
    db: DatabaseSession,
    current_user: CurrentUser,
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="最大返回数量")
) -> HealthDataListResponse:
    """
    获取指定类型的健康数据

    Args:
        data_type: 数据类型
        db: 数据库会话
        current_user: 当前用户
        start_date: 开始日期
        end_date: 结束日期
        limit: 最大返回数量

    Returns:
        健康数据列表
    """
    health_data_list = await health_crud.get_health_data_by_type(
        db=db,
        user_id=current_user.id,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return HealthDataListResponse(
        data=[HealthDataResponse.model_validate(d) for d in health_data_list],
        total=len(health_data_list),
        data_type=data_type
    )


@router.get("/data/{data_type}/latest", response_model=HealthDataResponse)
async def get_latest_health_data(
    data_type: str,
    db: DatabaseSession,
    current_user: CurrentUser
) -> HealthDataResponse:
    """
    获取最新的健康数据

    Args:
        data_type: 数据类型
        db: 数据库会话
        current_user: 当前用户

    Returns:
        最新的健康数据
    """
    health_data = await health_crud.get_latest_health_data(
        db=db,
        user_id=current_user.id,
        data_type=data_type
    )

    if not health_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for type: {data_type}"
        )

    return HealthDataResponse.model_validate(health_data)


@router.get("/summary", response_model=HealthSummaryResponse)
async def get_health_summary(
    db: DatabaseSession,
    current_user: CurrentUser,
    days: int = Query(7, ge=1, le=90, description="统计天数")
) -> HealthSummaryResponse:
    """
    获取健康数据摘要

    Args:
        db: 数据库会话
        current_user: 当前用户
        days: 统计天数(默认7天)

    Returns:
        健康数据摘要
    """
    summary = await health_crud.get_health_summary(
        db=db,
        user_id=current_user.id,
        days=days
    )

    return HealthSummaryResponse(
        user_id=current_user.id,
        period_days=days,
        summary=summary,
        generated_at=datetime.utcnow()
    )


@router.delete("/data/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_data(
    data_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser
):
    """
    删除健康数据

    Args:
        data_id: 数据ID
        db: 数据库会话
        current_user: 当前用户
    """
    success = await health_crud.delete_health_data(
        db=db,
        data_id=data_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health data {data_id} not found"
        )

    return None


@router.post("/sync", response_model=HealthSyncResponse)
async def sync_health_data(
    sync_request: HealthSyncRequest,
    db: DatabaseSession,
    current_user: CurrentUser
) -> HealthSyncResponse:
    """
    同步健康数据（从HealthKit/Google Fit）

    批量导入来自移动设备健康平台的数据，自动去重，支持多种数据类型。

    Args:
        sync_request: 同步请求数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        同步结果，包含成功数量和错误信息
    """
    synced_count = 0
    errors = []

    # 数据类型映射（从前端类型到数据库类型）
    type_mapping = {
        "sleep": HealthDataType.SLEEP_DURATION,
        "steps": HealthDataType.STEPS,
        "heart_rate": HealthDataType.HEART_RATE,
        "activity": HealthDataType.ACTIVE_CALORIES,
        "calories": HealthDataType.ACTIVE_CALORIES,
        "distance": HealthDataType.DISTANCE,
    }

    # 确定数据来源
    source = (
        HealthDataSource.APPLE_HEALTH
        if sync_request.data_source == "apple_health"
        else HealthDataSource.GOOGLE_FIT
    )

    health_data_list = []

    for record in sync_request.records:
        try:
            # 映射数据类型
            data_type = type_mapping.get(record.type, record.type)

            # 生成外部ID用于去重
            external_id = f"{sync_request.data_source}_{record.type}_{record.date}_{current_user.id}"

            # 检查是否已同步
            is_duplicate = await health_crud.check_duplicate_sync(
                db, current_user.id, external_id
            )
            if is_duplicate:
                continue

            # 解析日期
            try:
                recorded_at = datetime.fromisoformat(record.date)
            except ValueError:
                recorded_at = datetime.strptime(record.date, "%Y-%m-%d")

            # 处理value（可能是对象或数值）
            if isinstance(record.value, dict):
                # 对于activity类型，value是一个包含多个指标的对象
                # 为每个指标创建单独的记录
                for key, val in record.value.items():
                    sub_type = type_mapping.get(key, key)
                    sub_external_id = f"{external_id}_{key}"

                    # 检查子记录是否已同步
                    is_sub_duplicate = await health_crud.check_duplicate_sync(
                        db, current_user.id, sub_external_id
                    )
                    if is_sub_duplicate:
                        continue

                    health_data_obj = HealthData(
                        user_id=current_user.id,
                        data_type=sub_type,
                        value=float(val),
                        source=source,
                        unit=None,
                        recorded_at=recorded_at,
                        extra_data=record.metadata or {},
                        external_id=sub_external_id,
                        synced_at=datetime.utcnow()
                    )
                    health_data_list.append(health_data_obj)
            else:
                # 普通数值类型
                health_data_obj = HealthData(
                    user_id=current_user.id,
                    data_type=data_type,
                    value=float(record.value),
                    source=source,
                    unit=None,
                    recorded_at=recorded_at,
                    extra_data=record.metadata or {},
                    external_id=external_id,
                    synced_at=datetime.utcnow()
                )
                health_data_list.append(health_data_obj)

        except Exception as e:
            errors.append(f"处理记录 {record.type}@{record.date} 失败: {str(e)}")
            continue

    # 批量插入数据
    if health_data_list:
        try:
            created_data = await health_crud.create_health_data_batch(db, health_data_list)
            synced_count = len(created_data)
        except Exception as e:
            errors.append(f"批量插入失败: {str(e)}")
            return HealthSyncResponse(
                success=False,
                synced=0,
                errors=errors
            )

    return HealthSyncResponse(
        success=len(errors) == 0 or synced_count > 0,
        synced=synced_count,
        errors=errors
    )
