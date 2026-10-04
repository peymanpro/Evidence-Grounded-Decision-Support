from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ResearchQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    purpose: str = Field(min_length=1, max_length=2_000)


class ResearchExecutionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    purpose: str = Field(min_length=1, max_length=2_000)
    max_results: int = Field(default=5, ge=1, le=20)
    domains: list[str] = Field(default_factory=list, max_length=20)


class ResearchSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    max_results: int = Field(default=5, ge=1, le=20)
    domains: list[str] = Field(default_factory=list, max_length=20)


class ResearchSearchResult(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    snippet: str = Field(default="", max_length=2_000)
    publisher: str | None = Field(default=None, max_length=300)


class SourceDocument(BaseModel):
    url: HttpUrl
    status_code: int = Field(ge=100, le=599)
    content_type: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_length_bytes: int = Field(ge=0)
    retrieved_at: datetime
    etag: str | None = None
    last_modified: str | None = None


class NormalizedSource(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_length_bytes: int = Field(ge=0)


class ResearchSource(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    publisher: str | None = Field(default=None, max_length=300)
    retrieved_at: datetime | None = None
    status_code: int | None = Field(default=None, ge=100, le=599)
    content_type: str | None = None
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    content_length_bytes: int | None = Field(default=None, ge=0)
    snippet: str = ""


class ResearchFinding(BaseModel):
    source: ResearchSource
    claim: str = Field(min_length=1, max_length=5_000)
    confidence: float = Field(ge=0, le=1)
    supports_question: bool


class ResearchPlan(BaseModel):
    decision_id: str
    questions: list[ResearchQuestion]
    findings: list[ResearchFinding] = Field(default_factory=list)


class ResearchRun(BaseModel):
    question: ResearchQuestion
    provider: str
    started_at: datetime
    completed_at: datetime
    sources: list[ResearchSource] = Field(default_factory=list)
    documents: list[NormalizedSource] = Field(default_factory=list)
    fetch_errors: list[str] = Field(default_factory=list)
