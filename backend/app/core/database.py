"""
数据库连接和会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 将postgresql://转换为postgresql+asyncpg://
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# 创建异步引擎
if settings.is_development:
    # 开发环境: 使用NullPool,不需要连接池配置
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        poolclass=NullPool,
        echo=settings.SQL_ECHO,
    )
else:
    # 生产环境: 使用连接池
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        **settings.database_pool_config,
    )

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建Base类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖注入: 获取数据库会话

    使用方式:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库
    创建所有表(开发环境)
    """
    async with engine.begin() as conn:
        if settings.is_development:
            # 开发环境: 删除所有表并重新创建
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
