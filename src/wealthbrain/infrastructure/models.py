from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    messages: Mapped[list["MessageRecord"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageRecord.created_at",
    )


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    conversation: Mapped[ConversationRecord] = relationship(back_populates="messages")


class DecisionRecord(Base):
    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    decision: Mapped[str] = mapped_column(Text())
    decision_type: Mapped[str] = mapped_column(String(50))
    capital_at_risk: Mapped[float | None] = mapped_column(Float(), nullable=True)
    time_horizon_months: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AlternativeRecord(Base):
    __tablename__ = "decision_alternatives"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text(), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CriterionRecord(Base):
    __tablename__ = "decision_criteria"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    weight: Mapped[float] = mapped_column(Float())
    scale_min: Mapped[float] = mapped_column(Float(), default=0.0)
    scale_max: Mapped[float] = mapped_column(Float(), default=10.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionScoreRecord(Base):
    __tablename__ = "decision_scores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    criterion_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_criteria.id", ondelete="CASCADE"), index=True
    )
    alternative_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_alternatives.id", ondelete="CASCADE"), index=True
    )
    score: Mapped[float] = mapped_column(Float())


class EvidenceRecord(Base):
    __tablename__ = "decision_evidence"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str] = mapped_column(String(2_000))
    claim: Mapped[str] = mapped_column(Text())
    supports: Mapped[bool] = mapped_column(default=True)
    confidence: Mapped[float] = mapped_column(Float())
    quality: Mapped[str] = mapped_column(
        String(30), default="unverified"
    )
    provenance_publisher: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    provenance_retrieved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    provenance_status_code: Mapped[int | None] = mapped_column(
        nullable=True
    )
    provenance_content_type: Mapped[str | None] = mapped_column(
        String(120), nullable=True
    )
    provenance_content_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    provenance_content_length_bytes: Mapped[int | None] = mapped_column(
        nullable=True
    )
    provenance_excerpt: Mapped[str | None] = mapped_column(
        Text(), nullable=True
    )
    provenance_locator: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RiskRecord(Base):
    __tablename__ = "decision_risks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    probability: Mapped[float] = mapped_column(Float())
    impact: Mapped[float] = mapped_column(Float())
    risk_score: Mapped[float] = mapped_column(Float())
    mitigation: Mapped[str] = mapped_column(Text(), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JournalEntryRecord(Base):
    __tablename__ = "decision_journal_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    note: Mapped[str] = mapped_column(Text())
    outcome: Mapped[str | None] = mapped_column(Text(), nullable=True)
    happened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionAuditEventRecord(Base):
    __tablename__ = "decision_audit_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict[str, object]] = mapped_column(JSON(), default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KnowledgeCaseRecord(Base):
    __tablename__ = "knowledge_cases"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text())
    decision_type: Mapped[str] = mapped_column(String(50), index=True)
    alternatives: Mapped[list[str]] = mapped_column(JSON(), default=list)
    outcome: Mapped[str] = mapped_column(Text())
    lessons: Mapped[list[str]] = mapped_column(JSON(), default=list)
    source_url: Mapped[str | None] = mapped_column(String(2_000), nullable=True)
    source_publisher: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ResearchRunRecord(Base):
    __tablename__ = "research_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text())
    purpose: Mapped[str] = mapped_column(Text())
    provider: Mapped[str] = mapped_column(String(120))
    max_results: Mapped[int] = mapped_column()
    domains: Mapped[list[str]] = mapped_column(JSON(), default=list)
    sources: Mapped[list[dict[str, object]]] = mapped_column(JSON(), default=list)
    fetch_errors: Mapped[list[str]] = mapped_column(JSON(), default=list)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
