"""Rename projects to assessments and store review output.

Revision ID: 0004_assessments
Revises: 0003_remove_database_users
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_assessments"
down_revision = "0003_remove_database_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("projects", "assessments")
    with op.batch_alter_table("assessments") as batch_op:
        batch_op.add_column(sa.Column("question", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("audit_report", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("compliance_review", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("senior_review", sa.Text(), nullable=True))

    with op.batch_alter_table("operations") as batch_op:
        batch_op.alter_column(
            "project_id",
            new_column_name="assessment_id",
            existing_type=sa.String(length=36),
        )


def downgrade() -> None:
    with op.batch_alter_table("operations") as batch_op:
        batch_op.alter_column(
            "assessment_id",
            new_column_name="project_id",
            existing_type=sa.String(length=36),
        )

    with op.batch_alter_table("assessments") as batch_op:
        batch_op.drop_column("senior_review")
        batch_op.drop_column("compliance_review")
        batch_op.drop_column("audit_report")
        batch_op.drop_column("question")
    op.rename_table("assessments", "projects")
