"""Add parent question and trigger options columns to questions

Revision ID: d99b3a4c5b1f
Revises: bbdef0aeda07
Create Date: 2025-12-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd99b3a4c5b1f'
down_revision: Union[str, Sequence[str], None] = 'bbdef0aeda07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'questions',
        sa.Column('parent_question_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        constraint_name='fk_questions_parent_question_id',
        source_table='questions',
        referent_table='questions',
        local_cols=['parent_question_id'],
        remote_cols=['id'],
        ondelete='SET NULL',
    )
    op.add_column(
        'questions',
        sa.Column('trigger_options', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'fk_questions_parent_question_id',
        'questions',
        type_='foreignkey',
    )
    op.drop_column('questions', 'trigger_options')
    op.drop_column('questions', 'parent_question_id')

