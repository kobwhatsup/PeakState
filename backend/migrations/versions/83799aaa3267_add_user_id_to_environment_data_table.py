"""add user_id to environment_data table

Revision ID: 83799aaa3267
Revises: add6cd889839
Create Date: 2025-10-08 09:01:24.822210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '83799aaa3267'
down_revision: Union[str, None] = 'add6cd889839'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加user_id列(先设为可空)
    op.add_column('environment_data',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))

    # 删除现有数据(因为没有user_id)
    # 如果需要保留数据,需要手动关联到某个用户
    op.execute("DELETE FROM environment_data")

    # 设置为NOT NULL
    op.alter_column('environment_data', 'user_id', nullable=False)

    # 创建外键约束
    op.create_foreign_key(
        'fk_environment_data_user_id',
        'environment_data', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # 创建索引
    op.create_index('ix_environment_data_user_id', 'environment_data', ['user_id'])
    op.create_index('ix_environment_data_user_recorded', 'environment_data', ['user_id', 'recorded_at'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_environment_data_user_recorded', 'environment_data')
    op.drop_index('ix_environment_data_user_id', 'environment_data')

    # 删除外键
    op.drop_constraint('fk_environment_data_user_id', 'environment_data', type_='foreignkey')

    # 删除列
    op.drop_column('environment_data', 'user_id')
