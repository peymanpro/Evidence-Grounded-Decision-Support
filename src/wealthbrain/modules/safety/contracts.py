from typing import Literal

from pydantic import BaseModel, Field

SafetyIntent = Literal[
    "analysis",
    "recommendation",
    "external_action",
]


class SafetyCheckRequest(BaseModel):
    intent: SafetyIntent
    acknowledgement: bool = False


class SafetyCheckResponse(BaseModel):
    intent: SafetyIntent
    allowed: bool
    human_review_required: bool
    reasons: list[str] = Field(default_factory=list)
