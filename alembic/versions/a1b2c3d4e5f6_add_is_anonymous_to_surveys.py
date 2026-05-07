"""Add is_anonymous to surveys

Revision ID: a1b2c3d4e5f6
Revises: e4f96b9601ef
Create Date: 2026-05-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'e4f96b9601ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('surveys', sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('surveys', 'is_anonymous')
