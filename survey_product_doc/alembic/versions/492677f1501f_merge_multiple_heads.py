"""merge_multiple_heads

Revision ID: 492677f1501f
Revises: 2f4a1b7c3d88, e4f96b9601ef
Create Date: 2026-01-10 17:55:50.127421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '492677f1501f'
down_revision: Union[str, Sequence[str], None] = ('2f4a1b7c3d88', 'e4f96b9601ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
