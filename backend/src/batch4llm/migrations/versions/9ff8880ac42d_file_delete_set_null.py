"""file delete set null

Revision ID: 9ff8880ac42d
Revises: 7a2be2aa2bb0
Create Date: 2026-09-22 14:37:51.869848

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9ff8880ac42d"
down_revision: Union[str, None] = "7a2be2aa2bb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("batch_files", "file_id", existing_type=sa.INTEGER(), nullable=True)
    op.drop_constraint("batch_files_file_id_fkey", "batch_files", type_="foreignkey")
    op.create_foreign_key(
        "batch_files_file_id_fkey",
        "batch_files",
        "files",
        ["file_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("batch_tasks", "file_id", existing_type=sa.INTEGER(), nullable=True)
    op.drop_constraint("batch_tasks_file_id_fkey", "batch_tasks", type_="foreignkey")
    op.create_foreign_key(
        "batch_tasks_file_id_fkey",
        "batch_tasks",
        "files",
        ["file_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("batch_tasks_file_id_fkey", "batch_tasks", type_="foreignkey")
    op.create_foreign_key(
        "batch_tasks_file_id_fkey", "batch_tasks", "files", ["file_id"], ["id"]
    )
    op.alter_column(
        "batch_tasks", "file_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_constraint("batch_files_file_id_fkey", "batch_files", type_="foreignkey")
    op.create_foreign_key(
        "batch_files_file_id_fkey", "batch_files", "files", ["file_id"], ["id"]
    )
    op.alter_column(
        "batch_files", "file_id", existing_type=sa.INTEGER(), nullable=False
    )
