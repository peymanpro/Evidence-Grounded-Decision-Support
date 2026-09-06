from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class Materiality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisItem(BaseModel):
    """An immutable, explicitly classified input to decision analysis."""

    model_config = ConfigDict(frozen=True)

    statement: str = Field(min_length=1, max_length=10_000)

    @field_validator("statement")
    @classmethod
    def normalize_statement(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("statement must contain non-whitespace characters")
        return normalized


class Fact(AnalysisItem):
    """Information asserted as observed, with its origin kept explicit."""

    source: str | None = Field(default=None, min_length=1, max_length=500)


class Assumption(AnalysisItem):
    """An unverified input used by analysis rather than an established fact."""

    materiality: Materiality = Materiality.MEDIUM


class Calculation(BaseModel):
    """A deterministic quantitative result recorded separately from reasoning."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=200)
    formula: str = Field(min_length=1, max_length=2_000)
    result: float
    unit: str | None = Field(default=None, min_length=1, max_length=100)


class Reasoning(AnalysisItem):
    """An interpretation that must not be conflated with facts or calculations."""

    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class Uncertainty(AnalysisItem):
    """A known limitation that could materially change a decision."""

    materiality: Materiality = Materiality.MEDIUM


class DecisionOption(BaseModel):
    """A mutually comparable action within one decision category."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=200)
    decision_type: DecisionType
    description: str | None = Field(default=None, min_length=1, max_length=2_000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("name must contain non-whitespace characters")
        return normalized


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


class DecisionFrame(BaseModel):
    """The bounded alternatives and classified inputs for one user decision."""

    model_config = ConfigDict(frozen=True)

    context: DecisionContext
    options: tuple[DecisionOption, ...] = Field(min_length=1, max_length=10)
    facts: tuple[Fact, ...] = ()
    assumptions: tuple[Assumption, ...] = ()
    calculations: tuple[Calculation, ...] = ()
    reasoning: tuple[Reasoning, ...] = ()
    uncertainties: tuple[Uncertainty, ...] = ()

    @model_validator(mode="after")
    def validate_options(self) -> "DecisionFrame":
        option_names = [option.name.casefold() for option in self.options]
        if len(option_names) != len(set(option_names)):
            raise ValueError("decision options must be unique")
        if any(option.decision_type is not self.context.decision_type for option in self.options):
            raise ValueError("decision option categories must match the decision context")
        return self
