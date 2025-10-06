"""
认证API端点
用户注册、登录、令牌刷新、获取当前用户信息
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DatabaseSession
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.crud.user import (
    get_user_by_phone,
    create_user,
    authenticate_user,
    update_user,
)
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
)
from app.schemas.token import (
    Token,
    RefreshTokenRequest,
    RefreshTokenResponse,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: DatabaseSession,
) -> Token:
    """
    用户注册

    - 验证手机号格式
    - 检查手机号是否已注册
    - 创建用户并生成JWT令牌
    - 新用户自动获得7天试用期

    Args:
        user_data: 注册信息(手机号、密码、教练类型)
        db: 数据库会话

    Returns:
        JWT访问令牌和刷新令牌

    Raises:
        HTTPException: 手机号已注册时抛出400错误
    """
    # 检查手机号是否已存在
    existing_user = await get_user_by_phone(db, user_data.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    # 创建用户
    user = await create_user(db, user_data)

    # 生成令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: DatabaseSession,
) -> Token:
    """
    用户登录

    - 验证手机号和密码
    - 更新最后登录时间
    - 返回JWT令牌

    Args:
        credentials: 登录凭证(手机号、密码)
        db: 数据库会话

    Returns:
        JWT访问令牌和刷新令牌

    Raises:
        HTTPException: 凭证无效时抛出401错误
    """
    # 验证用户
    user = await authenticate_user(
        db,
        credentials.phone_number,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # 生成令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
) -> RefreshTokenResponse:
    """
    刷新访问令牌

    使用refresh_token获取新的access_token,延长会话时间

    Args:
        request: 刷新令牌请求

    Returns:
        新的访问令牌

    Raises:
        HTTPException: 刷新令牌无效时抛出401错误
    """
    try:
        user_id = verify_refresh_token(request.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成新的访问令牌
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    获取当前用户信息

    需要有效的JWT令牌

    Args:
        current_user: 当前认证用户(从JWT令牌解析)

    Returns:
        用户详细信息
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> UserResponse:
    """
    更新当前用户信息

    允许更新:
    - AI教练类型选择
    - 时区设置
    - 早报/晚间复盘配置

    Args:
        user_data: 更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        HTTPException: 更新失败时抛出500错误
    """
    updated_user = await update_user(db, current_user.id, user_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information",
        )

    return UserResponse.model_validate(updated_user)
