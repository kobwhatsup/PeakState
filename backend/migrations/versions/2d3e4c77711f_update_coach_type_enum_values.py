"""Update coach_type enum values

Revision ID: 2d3e4c77711f
Revises: cb135e4e4ab1
Create Date: 2025-10-07 00:54:22.809027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d3e4c77711f'
down_revision: Union[str, None] = 'cb135e4e4ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
