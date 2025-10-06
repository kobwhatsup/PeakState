"""
API路由包
"""

from fastapi import APIRouter
from app.api.routes import auth, chat

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["AI对话"]
)

__all__ = ["api_router"]
