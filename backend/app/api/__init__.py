"""
API路由包
"""

from fastapi import APIRouter
from app.api.routes import auth, chat, health

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth.router,
    tags=["认证"]
)

api_router.include_router(
    chat.router,
    tags=["AI对话"]
)

api_router.include_router(
    health.router,
    tags=["健康数据"]
)

__all__ = ["api_router"]
