"""
数据库连接和会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 将postgresql://转换为postgresql+asyncpg://并提取SSL参数
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# 提取SSL参数（如果存在）
import ssl as ssl_module
connect_args = {}

if "?" in database_url:
    base_url, params = database_url.split("?", 1)
    param_dict = dict(param.split("=") for param in params.split("&"))

    # 处理SSL参数
    if "sslmode" in param_dict:
        sslmode = param_dict.pop("sslmode")
        if sslmode in ("verify-ca", "verify-full", "require"):
            # asyncpg使用ssl_context而不是sslmode
            ssl_context = ssl_module.create_default_context()

            # 对于require模式，不验证主机名
            if sslmode == "require":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl_module.CERT_NONE

            if "sslrootcert" in param_dict:
                ssl_context.load_verify_locations(param_dict.pop("sslrootcert"))
            connect_args["ssl"] = ssl_context

    # 重建URL（去除SSL参数）
    if param_dict:
        ASYNC_DATABASE_URL = base_url + "?" + "&".join(f"{k}={v}" for k, v in param_dict.items())
    else:
        ASYNC_DATABASE_URL = base_url
else:
    ASYNC_DATABASE_URL = database_url

# 创建异步引擎
if settings.is_development:
    # 开发环境: 使用NullPool,不需要连接池配置
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        poolclass=NullPool,
        echo=settings.SQL_ECHO,
        connect_args=connect_args,
    )
else:
    # 生产环境: 使用连接池
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        connect_args=connect_args,
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
