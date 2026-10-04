from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class HistoricalCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1, max_length=10_000)
    decision_type: str = Field(min_length=1, max_length=50)
    alternatives: list[str] = Field(default_factory=list, max_length=20)
    outcome: str = Field(min_length=1, max_length=10_000)
    lessons: list[str] = Field(default_factory=list, max_length=20)
    source_url: HttpUrl | None = None
    source_publisher: str | None = Field(default=None, max_length=300)
    is_synthetic: bool = True


class HistoricalCaseResponse(HistoricalCaseCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class HistoricalCaseSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    decision_type: str | None = Field(default=None, max_length=50)
    limit: int = Field(default=10, ge=1, le=50)


class HistoricalCaseSearchResult(BaseModel):
    case: HistoricalCaseResponse
    relevance: float = Field(ge=0, le=1)
