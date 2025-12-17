"""add start and end time columns to surveys"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0d7e8c9b1a37"
down_revision = "f1b3a24c5e8c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "surveys",
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "surveys",
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_column("surveys", "end_time")
    op.drop_column("surveys", "start_time")

