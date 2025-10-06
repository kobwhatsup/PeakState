"""
Alembic迁移环境配置
从app.core.config动态获取数据库URL
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 导入配置和模型
from app.core.config import settings
from app.core.database import Base

# 导入所有模型以便自动检测
from app.models.user import User
from app.models.conversation import Conversation
from app.models.health_data import HealthData

# Alembic Config对象
config = context.config

# 从settings获取数据库URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 配置Python日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置target_metadata用于autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式运行迁移

    此模式仅使用URL配置context,不创建Engine
    适用于生成SQL脚本而不实际连接数据库
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 比较列类型变化
        compare_server_default=True,  # 比较默认值变化
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式运行迁移

    此模式创建Engine并连接数据库
    适用于实际执行迁移操作
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 比较列类型变化
            compare_server_default=True,  # 比较默认值变化
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
