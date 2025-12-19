"""Normalize question type enum values to lowercase"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2f4a1b7c3d88"
down_revision = "1b3f6a2d7c8e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE questions SET `type` = 'sort_order' WHERE `type` = 'SORT_ORDER';"
    )
    op.execute(
        "UPDATE questions SET `type` = 'conditional' WHERE `type` = 'CONDITIONAL';"
    )
    op.execute(
        "ALTER TABLE questions "
        "MODIFY COLUMN `type` ENUM('single_choice','multi_choice','text_input','number_input','sort_order','conditional') NOT NULL;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "MODIFY COLUMN `type` ENUM('SINGLE_CHOICE','MULTI_CHOICE','TEXT_INPUT','NUMBER_INPUT','SORT_ORDER','CONDITIONAL') NOT NULL;"
    )
    op.execute(
        "UPDATE questions SET `type` = 'SORT_ORDER' WHERE `type` = 'sort_order';"
    )
    op.execute(
        "UPDATE questions SET `type` = 'CONDITIONAL' WHERE `type` = 'conditional';"
    )

