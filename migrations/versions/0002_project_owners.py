"""Add users and require project owners.

Revision ID: 0002_project_owners
Revises: 0001_initial_schema
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_project_owners"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    project_count = connection.execute(sa.text("SELECT COUNT(*) FROM projects")).scalar_one()
    if project_count:
        raise RuntimeError(
            "Cannot add required project owners while existing projects lack user records. "
            "Create matching users and backfill owner_id before migrating."
        )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user", sa.String(length=36), nullable=False),
        sa.Column("safe_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user"),
    )

    with op.batch_alter_table("projects", recreate="always") as batch_op:
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.String(length=128),
            type_=sa.String(length=36),
            existing_nullable=True,
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_projects_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("projects", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_projects_owner_id_users", type_="foreignkey")
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.String(length=36),
            type_=sa.String(length=128),
            existing_nullable=False,
            nullable=True,
        )

    op.drop_table("users")
