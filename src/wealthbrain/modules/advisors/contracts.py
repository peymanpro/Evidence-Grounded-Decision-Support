from typing import Literal

from pydantic import BaseModel, Field

AdvisorRole = Literal[
    "evidence",
    "quantitative",
    "risk",
    "challenge",
]


class AdvisorView(BaseModel):
    name: str
    focus: str
    observations: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


class AdvisorPanel(BaseModel):
    views: list[AdvisorView] = Field(default_factory=list)


class AdvisorRequest(BaseModel):
    role: AdvisorRole
    max_tokens: int = Field(default=1_500, ge=1, le=4_000)


class AdvisorResponse(BaseModel):
    role: AdvisorRole
    provider: str
    model: str
    content: str = Field(min_length=1)
    human_review_required: bool = True
