"""Add evidence provenance fields.

Revision ID: 0004_evidence_provenance
Revises: 0003_decision_audit_events
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_evidence_provenance"
down_revision = "0003_decision_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decision_evidence",
        sa.Column(
            "quality",
            sa.String(length=30),
            server_default="unverified",
            nullable=False,
        ),
    )
    op.add_column(
        "decision_evidence",
        sa.Column("provenance_publisher", sa.String(length=300), nullable=True),
    )
    op.add_column(
        "decision_evidence",
        sa.Column(
            "provenance_retrieved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "decision_evidence",
        sa.Column("provenance_status_code", sa.Integer(), nullable=True),
    )
    op.add_column(
        "decision_evidence",
        sa.Column(
            "provenance_content_type",
            sa.String(length=120),
            nullable=True,
        ),
    )
    op.add_column(
        "decision_evidence",
        sa.Column(
            "provenance_content_sha256",
            sa.String(length=64),
            nullable=True,
        ),
    )
    op.add_column(
        "decision_evidence",
        sa.Column(
            "provenance_content_length_bytes",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "decision_evidence",
        sa.Column("provenance_excerpt", sa.Text(), nullable=True),
    )
    op.add_column(
        "decision_evidence",
        sa.Column(
            "provenance_locator",
            sa.String(length=500),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_decision_evidence_provenance_content_sha256",
        "decision_evidence",
        ["provenance_content_sha256"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_decision_evidence_provenance_content_sha256",
        table_name="decision_evidence",
    )
    op.drop_column("decision_evidence", "provenance_locator")
    op.drop_column("decision_evidence", "provenance_excerpt")
    op.drop_column("decision_evidence", "provenance_content_length_bytes")
    op.drop_column("decision_evidence", "provenance_content_sha256")
    op.drop_column("decision_evidence", "provenance_content_type")
    op.drop_column("decision_evidence", "provenance_status_code")
    op.drop_column("decision_evidence", "provenance_retrieved_at")
    op.drop_column("decision_evidence", "provenance_publisher")
    op.drop_column("decision_evidence", "quality")
