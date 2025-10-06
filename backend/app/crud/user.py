"""
用户CRUD操作
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister, UserUpdate
from app.core.security import get_password_hash, verify_password


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    根据ID获取用户

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        用户对象或None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone_number: str) -> Optional[User]:
    """
    根据手机号获取用户

    Args:
        db: 数据库会话
        phone_number: 手机号

    Returns:
        用户对象或None
    """
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRegister) -> User:
    """
    创建新用户

    Args:
        db: 数据库会话
        user_data: 用户注册数据

    Returns:
        创建的用户对象
    """
    # 创建用户对象
    db_user = User(
        phone_number=user_data.phone_number,
        hashed_password=get_password_hash(user_data.password),
        coach_selection=user_data.coach_selection,
        is_verified=False,  # 手机号未验证
        is_trial=True,  # 新用户默认开启试用
        trial_end_date=datetime.utcnow() + timedelta(days=7),  # 7天试用
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    user_data: UserUpdate
) -> Optional[User]:
    """
    更新用户信息

    Args:
        db: 数据库会话
        user_id: 用户ID
        user_data: 更新数据

    Returns:
        更新后的用户对象或None
    """
    # 获取用户
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    phone_number: str,
    password: str
) -> Optional[User]:
    """
    验证用户登录

    Args:
        db: 数据库会话
        phone_number: 手机号
        password: 密码

    Returns:
        验证成功返回用户对象,失败返回None
    """
    user = await get_user_by_phone(db, phone_number)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return user


async def update_subscription(
    db: AsyncSession,
    user_id: UUID,
    subscription_type: str,
    duration_days: int
) -> Optional[User]:
    """
    更新用户订阅状态

    Args:
        db: 数据库会话
        user_id: 用户ID
        subscription_type: 订阅类型(monthly/yearly)
        duration_days: 订阅时长(天)

    Returns:
        更新后的用户对象或None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # 计算订阅结束时间
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)

    # 更新订阅信息
    user.is_subscribed = True
    user.subscription_type = subscription_type
    user.subscription_start_date = start_date
    user.subscription_end_date = end_date

    # 取消试用状态
    user.is_trial = False

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    停用用户账号

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        停用后的用户对象或None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def activate_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    激活用户账号

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        激活后的用户对象或None
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user
