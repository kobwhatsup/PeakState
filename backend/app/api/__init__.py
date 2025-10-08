"""
API路由包
"""

from fastapi import APIRouter
from app.api.routes import auth, chat, health, cache, energy, weather, environment

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth.router,
    tags=["认证"]
)

api_router.include_router(chat.router)

api_router.include_router(
    health.router,
    tags=["健康数据"]
)

api_router.include_router(
    energy.router,
    tags=["精力管理"]
)

api_router.include_router(
    weather.router,
    prefix="/weather",
    tags=["天气服务"]
)

api_router.include_router(
    environment.router,
    prefix="/environment",
    tags=["环境数据"]
)

api_router.include_router(cache.router)

__all__ = ["api_router"]
