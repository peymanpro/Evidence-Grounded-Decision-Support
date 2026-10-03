"""Add decision audit events.

Revision ID: 0003_decision_audit_events
Revises: 0002_decision_workspace
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_decision_audit_events"
down_revision = "0002_decision_workspace"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decision_audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
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
        "ix_decision_audit_events_decision_id",
        "decision_audit_events",
        ["decision_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_decision_audit_events_decision_id",
        table_name="decision_audit_events",
    )
    op.drop_table("decision_audit_events")
