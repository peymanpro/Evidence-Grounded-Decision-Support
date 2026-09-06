from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from wealthbrain.domain.decisions import DecisionContext

MAX_INTERVIEW_QUESTIONS = 3


class WorkflowStage(StrEnum):
    INTERVIEW = "interview"
    RESEARCH = "research"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    RISK_ANALYSIS = "risk_analysis"
    CRITIQUE = "critique"
    SYNTHESIS = "synthesis"


class ResearchTrigger(StrEnum):
    CURRENT_INFORMATION = "current_information"
    MARKET_CONDITIONS = "market_conditions"
    REGULATION = "regulation"
    IRAN_SPECIFIC = "iran_specific"


class AdvisoryRequest(BaseModel):
    """The user request supplied to the deterministic workflow planner."""

    model_config = ConfigDict(frozen=True)

    context: DecisionContext
    request_text: str = Field(min_length=1, max_length=20_000)
    questions_asked: int = Field(default=0, ge=0, le=MAX_INTERVIEW_QUESTIONS)

    @field_validator("request_text")
    @classmethod
    def normalize_request_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("request_text must contain non-whitespace characters")
        return normalized


class OrchestrationPlan(BaseModel):
    """A bounded, inspectable plan; execution belongs to later phases."""

    model_config = ConfigDict(frozen=True)

    stages: tuple[WorkflowStage, ...] = Field(min_length=2)
    interview_question_budget: int = Field(ge=0, le=MAX_INTERVIEW_QUESTIONS)
    research_triggers: tuple[ResearchTrigger, ...] = ()

    @model_validator(mode="after")
    def validate_stage_order(self) -> "OrchestrationPlan":
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("workflow stages must be unique")
        if self.stages[-2:] != (WorkflowStage.CRITIQUE, WorkflowStage.SYNTHESIS):
            raise ValueError("critique must occur immediately before synthesis")
        has_research = WorkflowStage.RESEARCH in self.stages
        if has_research != bool(self.research_triggers):
            raise ValueError("research stages and research triggers must agree")
        return self
