"""Add the decision workspace tables.

Revision ID: 0002_decision_workspace
Revises: 0001_conversations
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_decision_workspace"
down_revision = "0001_conversations"
branch_labels = None
depends_on = None


def _timestamp_column() -> sa.Column[sa.DateTime]:
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("decision_type", sa.String(length=50), nullable=False),
        sa.Column("capital_at_risk", sa.Float(), nullable=True),
        sa.Column("time_horizon_months", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        _timestamp_column(),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decisions_conversation_id",
        "decisions",
        ["conversation_id"],
    )

    op.create_table(
        "decision_alternatives",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        _timestamp_column(),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_alternatives_decision_id",
        "decision_alternatives",
        ["decision_id"],
    )

    op.create_table(
        "decision_criteria",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("scale_min", sa.Float(), nullable=False),
        sa.Column("scale_max", sa.Float(), nullable=False),
        _timestamp_column(),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_criteria_decision_id",
        "decision_criteria",
        ["decision_id"],
    )

    op.create_table(
        "decision_scores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("criterion_id", sa.Uuid(), nullable=False),
        sa.Column("alternative_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["criterion_id"],
            ["decision_criteria.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["alternative_id"],
            ["decision_alternatives.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_scores_decision_id",
        "decision_scores",
        ["decision_id"],
    )
    op.create_index(
        "ix_decision_scores_criterion_id",
        "decision_scores",
        ["criterion_id"],
    )
    op.create_index(
        "ix_decision_scores_alternative_id",
        "decision_scores",
        ["alternative_id"],
    )

    op.create_table(
        "decision_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("source_url", sa.String(length=2000), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("supports", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        _timestamp_column(),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_evidence_decision_id",
        "decision_evidence",
        ["decision_id"],
    )

    op.create_table(
        "decision_risks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("impact", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("mitigation", sa.Text(), nullable=False),
        _timestamp_column(),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_risks_decision_id",
        "decision_risks",
        ["decision_id"],
    )

    op.create_table(
        "decision_journal_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column(
            "happened_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        _timestamp_column(),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decision_journal_entries_decision_id",
        "decision_journal_entries",
        ["decision_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_decision_journal_entries_decision_id",
        table_name="decision_journal_entries",
    )
    op.drop_table("decision_journal_entries")
    op.drop_index(
        "ix_decision_risks_decision_id",
        table_name="decision_risks",
    )
    op.drop_table("decision_risks")
    op.drop_index(
        "ix_decision_evidence_decision_id",
        table_name="decision_evidence",
    )
    op.drop_table("decision_evidence")
    op.drop_index(
        "ix_decision_scores_alternative_id",
        table_name="decision_scores",
    )
    op.drop_index(
        "ix_decision_scores_criterion_id",
        table_name="decision_scores",
    )
    op.drop_index(
        "ix_decision_scores_decision_id",
        table_name="decision_scores",
    )
    op.drop_table("decision_scores")
    op.drop_index(
        "ix_decision_criteria_decision_id",
        table_name="decision_criteria",
    )
    op.drop_table("decision_criteria")
    op.drop_index(
        "ix_decision_alternatives_decision_id",
        table_name="decision_alternatives",
    )
    op.drop_table("decision_alternatives")
    op.drop_index(
        "ix_decisions_conversation_id",
        table_name="decisions",
    )
    op.drop_table("decisions")
