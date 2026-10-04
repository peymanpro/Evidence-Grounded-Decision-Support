from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, ValidationInfo, field_validator

from wealthbrain.modules.evidence.contracts import EvidenceSufficiency


class DecisionCreate(BaseModel):
    conversation_id: UUID | None = None
    decision: str = Field(min_length=1, max_length=10_000)
    decision_type: str = Field(default="other", min_length=1, max_length=50)
    capital_at_risk: float | None = Field(default=None, ge=0)
    time_horizon_months: int | None = Field(default=None, ge=1, le=1_200)

    @field_validator("decision")
    @classmethod
    def normalize_decision(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("decision must contain non-whitespace characters")
        return normalized


class DecisionResponse(DecisionCreate):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlternativeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5_000)


class AlternativeResponse(AlternativeCreate):
    id: UUID
    decision_id: UUID

    model_config = {"from_attributes": True}


class CriterionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    weight: float = Field(gt=0)
    scale_min: float = 0.0
    scale_max: float = 10.0

    @field_validator("scale_max")
    @classmethod
    def validate_scale(cls, value: float, info: ValidationInfo) -> float:
        minimum = info.data.get("scale_min", 0.0)
        if value <= minimum:
            raise ValueError("scale_max must be greater than scale_min")
        return value


class CriterionResponse(CriterionCreate):
    id: UUID
    decision_id: UUID

    model_config = {"from_attributes": True}


class ScoreCreate(BaseModel):
    criterion_id: UUID
    alternative_id: UUID
    score: float


class EvidenceProvenance(BaseModel):
    publisher: str | None = Field(default=None, max_length=300)
    retrieved_at: datetime | None = None
    status_code: int | None = Field(default=None, ge=100, le=599)
    content_type: str | None = Field(default=None, max_length=120)
    content_sha256: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    content_length_bytes: int | None = Field(default=None, ge=0)
    excerpt: str | None = Field(default=None, max_length=5_000)
    locator: str | None = Field(default=None, max_length=500)


class EvidenceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    source_url: HttpUrl
    claim: str = Field(min_length=1, max_length=5_000)
    supports: bool = True
    confidence: float = Field(default=0.5, ge=0, le=1)
    quality: Literal[
        "unverified",
        "partially_verified",
        "verified",
        "challenged",
    ] = "unverified"
    provenance: EvidenceProvenance = Field(default_factory=EvidenceProvenance)


class EvidenceResponse(EvidenceCreate):
    id: UUID
    decision_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    probability: float = Field(ge=0, le=1)
    impact: float = Field(ge=0, le=10)
    mitigation: str = Field(default="", max_length=5_000)


class RiskResponse(RiskCreate):
    id: UUID
    decision_id: UUID
    risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryCreate(BaseModel):
    note: str = Field(min_length=1, max_length=10_000)
    outcome: str | None = Field(default=None, max_length=5_000)
    happened_at: datetime | None = None


class JournalEntryResponse(JournalEntryCreate):
    id: UUID
    decision_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditEventResponse(BaseModel):
    id: UUID
    decision_id: UUID
    event_type: str
    payload: dict[str, object]
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionScore(BaseModel):
    alternative_id: UUID
    alternative_name: str
    weighted_score: float
    normalized_score: float


class QuantitativeAnalysis(BaseModel):
    scores: list[DecisionScore]
    preferred_alternative_id: UUID | None
    preferred_alternative_name: str | None
    sensitivity: dict[str, dict[str, float]]
    confidence: float = Field(ge=0, le=1)


class RiskAnalysis(BaseModel):
    total_risk_score: float = Field(ge=0)
    high_risk_count: int = Field(ge=0)
    risks: list[dict[str, object]]


class CritiqueResult(BaseModel):
    strengths: list[str]
    concerns: list[str]
    missing_information: list[str]
    human_review_required: bool


class SynthesisResult(BaseModel):
    decision_id: UUID
    preferred_alternative: str | None
    evidence_summary: list[str]
    quantitative_summary: list[str]
    risk_summary: list[str]
    uncertainty: list[str]
    next_steps: list[str]
    human_review_required: bool = True


class DecisionReport(BaseModel):
    decision: DecisionResponse
    alternatives: list[AlternativeResponse]
    criteria: list[CriterionResponse]
    evidence: list[EvidenceResponse]
    risks: list[RiskResponse]
    score_count: int = Field(ge=0)
    quantitative: QuantitativeAnalysis
    risk_analysis: RiskAnalysis
    critique: CritiqueResult
    synthesis: SynthesisResult
    evidence_sufficiency: EvidenceSufficiency = Field(
        default_factory=lambda: EvidenceSufficiency(
            supporting_count=0,
            challenging_count=0,
            verified_supporting_count=0,
            source_domain_count=0,
            score=0.0,
            sufficient=False,
        )
    )
