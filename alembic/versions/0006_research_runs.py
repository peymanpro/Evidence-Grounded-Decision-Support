"""Persist research run metadata.

Revision ID: 0006_research_runs
Revises: 0005_knowledge_cases
"""

import sqlalchemy as sa
from alembic import op

revision = "0006_research_runs"
down_revision = "0005_knowledge_cases"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("max_results", sa.Integer(), nullable=False),
        sa.Column("domains", sa.JSON(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("fetch_errors", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_runs_decision_id",
        "research_runs",
        ["decision_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_research_runs_decision_id",
        table_name="research_runs",
    )
    op.drop_table("research_runs")
