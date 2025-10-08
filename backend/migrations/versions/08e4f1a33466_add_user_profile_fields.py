"""add_user_profile_fields

Revision ID: 08e4f1a33466
Revises: 2d3e4c77711f
Create Date: 2025-10-07 13:12:26.028041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08e4f1a33466'
down_revision: Union[str, None] = '2d3e4c77711f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加用户画像字段
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True, comment='年龄'))
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True, comment='性别(male/female/other/prefer_not_to_say)'))
    op.add_column('users', sa.Column('occupation', sa.String(length=100), nullable=True, comment='职业'))
    op.add_column('users', sa.Column('health_goals', sa.String(length=500), nullable=True, comment='健康目标(逗号分隔)'))


def downgrade() -> None:
    # 移除用户画像字段
    op.drop_column('users', 'health_goals')
    op.drop_column('users', 'occupation')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')
