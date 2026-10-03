from pydantic import BaseModel, Field, HttpUrl


class ResearchQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    purpose: str = Field(min_length=1, max_length=2_000)


class ResearchSource(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    publisher: str | None = Field(default=None, max_length=300)
    retrieved_at: str | None = None


class ResearchFinding(BaseModel):
    source: ResearchSource
    claim: str = Field(min_length=1, max_length=5_000)
    confidence: float = Field(ge=0, le=1)
    supports_question: bool


class ResearchPlan(BaseModel):
    decision_id: str
    questions: list[ResearchQuestion]
    findings: list[ResearchFinding] = []
