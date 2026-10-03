from pydantic import BaseModel, Field


class QualityCheck(BaseModel):
    name: str
    score: float = Field(ge=0, le=1)
    explanation: str


class DecisionQualityReport(BaseModel):
    overall_score: float = Field(ge=0, le=1)
    checks: list[QualityCheck] = Field(default_factory=list)
    blocking_issues: list[str] = Field(default_factory=list)
