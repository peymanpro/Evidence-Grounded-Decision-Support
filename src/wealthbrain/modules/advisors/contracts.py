from pydantic import BaseModel, Field


class AdvisorView(BaseModel):
    name: str
    focus: str
    observations: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


class AdvisorPanel(BaseModel):
    views: list[AdvisorView] = Field(default_factory=list)
