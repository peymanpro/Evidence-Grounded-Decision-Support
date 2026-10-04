"""Add structured historical knowledge cases.

Revision ID: 0005_knowledge_cases
Revises: 0004_evidence_provenance
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_knowledge_cases"
down_revision = "0004_evidence_provenance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("decision_type", sa.String(length=50), nullable=False),
        sa.Column("alternatives", sa.JSON(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("lessons", sa.JSON(), nullable=False),
        sa.Column("source_url", sa.String(length=2000), nullable=True),
        sa.Column("source_publisher", sa.String(length=300), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_cases_decision_type",
        "knowledge_cases",
        ["decision_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_cases_decision_type",
        table_name="knowledge_cases",
    )
    op.drop_table("knowledge_cases")
