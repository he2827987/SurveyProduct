"""add organization columns to survey answers

Revision ID: f1b3a24c5e8c
Revises: d99b3a4c5b1f
Create Date: 2025-12-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f1b3a24c5e8c"
down_revision = "d99b3a4c5b1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "survey_answers",
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
    )
    op.add_column(
        "survey_answers",
        sa.Column("organization_name", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("survey_answers", "organization_name")
    op.drop_column("survey_answers", "organization_id")

