from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DecisionType(StrEnum):
    INVESTMENT = "investment"
    PURCHASE = "purchase"
    BUSINESS = "business"
    CAREER = "career"
    CAPITAL_ALLOCATION = "capital_allocation"
    OTHER = "other"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionContext(BaseModel):
    """A bounded decision described within one conversation, never a user profile."""

    conversation_id: UUID
    decision: str = Field(min_length=1, max_length=10_000)
    decision_type: DecisionType = DecisionType.OTHER
    capital_at_risk: float | None = Field(default=None, ge=0)
    time_horizon_months: int | None = Field(default=None, ge=1, le=1_200)

    @field_validator("decision")
    @classmethod
    def normalize_decision(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("decision must contain non-whitespace characters")
        return normalized
