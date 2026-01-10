"""Add enum values for sorting and conditional question types"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1b3f6a2d7c8e"
down_revision = "f1b3a24c5e8c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "MODIFY COLUMN `type` ENUM('SINGLE_CHOICE','MULTI_CHOICE','TEXT_INPUT','NUMBER_INPUT','SORT_ORDER','CONDITIONAL') NOT NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "MODIFY COLUMN `type` ENUM('SINGLE_CHOICE','MULTI_CHOICE','TEXT_INPUT','NUMBER_INPUT') NOT NULL"
    )

