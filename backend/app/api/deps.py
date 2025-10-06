"""
API依赖注入函数
"""

from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_access_token
from app.crud.user import get_user_by_id
from app.models.user import User

# HTTP Bearer令牌认证
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    获取当前认证用户

    从Authorization header中提取JWT令牌并验证,返回用户对象

    Args:
        credentials: Bearer令牌
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 令牌无效或用户不存在时抛出401错误
    """
    # 提取令牌
    token = credentials.credentials

    # 验证令牌并提取用户ID
    try:
        user_id = verify_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户
    user = await get_user_by_id(db, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前激活用户

    额外检查用户是否有访问权限(订阅或试用中)

    Args:
        current_user: 当前用户

    Returns:
        当前激活用户

    Raises:
        HTTPException: 用户无访问权限时抛出403错误
    """
    if not current_user.has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew your subscription.",
        )

    return current_user


# 类型别名,方便使用
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
