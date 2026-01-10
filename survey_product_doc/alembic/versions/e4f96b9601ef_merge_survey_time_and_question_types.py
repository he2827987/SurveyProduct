"""merge survey time and question types

Revision ID: e4f96b9601ef
Revises: 0d7e8c9b1a37, 1b3f6a2d7c8e
Create Date: 2026-01-08 22:05:40.644563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f96b9601ef'
down_revision: Union[str, Sequence[str], None] = ('0d7e8c9b1a37', '1b3f6a2d7c8e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
