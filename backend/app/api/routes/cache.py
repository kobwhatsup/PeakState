"""
缓存管理API
提供缓存统计、监控和管理接口
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.ai.response_cache import get_response_cache_manager
from app.core.redis_client import get_redis_manager


router = APIRouter(prefix="/cache", tags=["缓存管理"])


# ============ 依赖注入 ============
CurrentUser = Annotated[User, Depends(get_current_user)]


# ============ Response Models ============

class CacheStatsResponse(BaseModel):
    """缓存统计响应"""
    total_requests: int
    total_hits: int
    cache_hit_rate_percent: float
    l1_hits: int
    l1_hit_rate_percent: float
    l2_hits: int
    l2_hit_rate_percent: float
    l3_hits: int
    l3_hit_rate_percent: float
    cache_misses: int
    cache_miss_rate_percent: float
    total_cost_saved_usd: float
    total_latency_saved_ms: float
    avg_cached_response_time_ms: float
    avg_uncached_response_time_ms: float


class RedisStatsResponse(BaseModel):
    """Redis统计响应"""
    connected: bool
    db: int
    total_keys: int
    total_commands: int
    keyspace_hits: int
    keyspace_misses: int
    hit_rate_percent: float
    memory_used_human: str
    evicted_keys: int


class SuccessResponse(BaseModel):
    """成功响应"""
    message: str
    details: dict = {}


# ============ API端点 ============

@router.get(
    "/stats",
    response_model=CacheStatsResponse,
    summary="获取缓存统计",
    description="获取三层缓存的详细统计信息，包括命中率、成本节省等"
)
async def get_cache_stats(
    current_user: CurrentUser
):
    """
    获取缓存统计信息

    返回:
    - 总请求数
    - L1/L2/L3各层命中率
    - 总成本节省
    - 平均响应时间
    """
    try:
        cache_manager = await get_response_cache_manager()

        stats = cache_manager.get_stats()

        # 如果还没有请求，返回默认值
        if "message" in stats:
            return CacheStatsResponse(
                total_requests=0,
                total_hits=0,
                cache_hit_rate_percent=0.0,
                l1_hits=0,
                l1_hit_rate_percent=0.0,
                l2_hits=0,
                l2_hit_rate_percent=0.0,
                l3_hits=0,
                l3_hit_rate_percent=0.0,
                cache_misses=0,
                cache_miss_rate_percent=0.0,
                total_cost_saved_usd=0.0,
                total_latency_saved_ms=0.0,
                avg_cached_response_time_ms=0.0,
                avg_uncached_response_time_ms=0.0
            )

        return CacheStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.get(
    "/redis/stats",
    response_model=RedisStatsResponse,
    summary="获取Redis统计",
    description="获取Redis服务器的详细统计信息"
)
async def get_redis_stats(
    current_user: CurrentUser
):
    """
    获取Redis统计信息

    返回:
    - 连接状态
    - 键数量
    - 命中率
    - 内存使用
    """
    try:
        redis_manager = await get_redis_manager()

        stats = await redis_manager.get_stats()

        # 处理错误情况
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Redis stats error: {stats['error']}"
            )

        return RedisStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Redis stats: {str(e)}"
        )


@router.post(
    "/invalidate/me",
    response_model=SuccessResponse,
    summary="清空当前用户缓存",
    description="清空当前登录用户的所有缓存数据（Redis + Qdrant）"
)
async def invalidate_my_cache(
    current_user: CurrentUser
):
    """
    清空当前用户的缓存

    包括:
    - Redis L1缓存
    - Qdrant L2缓存
    """
    try:
        cache_manager = await get_response_cache_manager()

        await cache_manager.invalidate_user_cache(str(current_user.id))

        return SuccessResponse(
            message="Cache invalidated successfully",
            details={
                "user_id": str(current_user.id),
                "layers_cleared": ["L1_Redis", "L2_Qdrant"]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate cache: {str(e)}"
        )


@router.get(
    "/health",
    response_model=SuccessResponse,
    summary="缓存健康检查",
    description="检查缓存系统是否正常运行"
)
async def cache_health_check(
    current_user: CurrentUser
):
    """
    缓存系统健康检查

    检查:
    - Redis连接
    - Qdrant连接
    - 缓存管理器状态
    """
    health_status = {
        "redis": "unknown",
        "qdrant": "unknown",
        "cache_manager": "unknown"
    }

    try:
        # 检查Redis
        try:
            redis_manager = await get_redis_manager()
            await redis_manager.client.ping()
            health_status["redis"] = "healthy"
        except Exception as e:
            health_status["redis"] = f"unhealthy: {str(e)}"

        # 检查Qdrant
        try:
            cache_manager = await get_response_cache_manager()
            await cache_manager.initialize()

            # 测试Qdrant连接
            cache_manager.qdrant_client.get_collections()
            health_status["qdrant"] = "healthy"
        except Exception as e:
            health_status["qdrant"] = f"unhealthy: {str(e)}"

        # 检查缓存管理器
        try:
            if cache_manager._initialized:
                health_status["cache_manager"] = "healthy"
            else:
                health_status["cache_manager"] = "not_initialized"
        except Exception as e:
            health_status["cache_manager"] = f"unhealthy: {str(e)}"

        # 判断整体状态
        all_healthy = all(
            status == "healthy"
            for status in health_status.values()
        )

        if not all_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Cache system partially unhealthy", "status": health_status}
            )

        return SuccessResponse(
            message="Cache system healthy",
            details=health_status
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get(
    "/info",
    response_model=SuccessResponse,
    summary="缓存系统信息",
    description="获取缓存系统的配置和状态信息"
)
async def get_cache_info(
    current_user: CurrentUser
):
    """
    获取缓存系统信息

    包括:
    - 缓存配置
    - 系统状态
    - 性能指标
    """
    try:
        cache_manager = await get_response_cache_manager()
        redis_manager = await get_redis_manager()

        # 收集信息
        info = {
            "cache_enabled": True,
            "cache_layers": {
                "L1": {
                    "type": "Redis",
                    "description": "Exact match cache",
                    "ttl_hours": 24,
                    "expected_hit_rate": "15-20%"
                },
                "L2": {
                    "type": "Qdrant",
                    "description": "Semantic similarity cache",
                    "ttl_days": 7,
                    "similarity_threshold": 0.92,
                    "expected_hit_rate": "8-12%"
                },
                "L3": {
                    "type": "Qdrant",
                    "description": "Knowledge base pre-answers",
                    "ttl": "permanent",
                    "similarity_threshold": 0.88,
                    "expected_hit_rate": "2-5%"
                }
            },
            "cache_manager_initialized": cache_manager._initialized,
            "redis_connected": redis_manager._connected,
            "sentence_transformer_loaded": cache_manager.sentence_transformer is not None if cache_manager._initialized else False
        }

        return SuccessResponse(
            message="Cache system info",
            details=info
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache info: {str(e)}"
        )
