from pydantic import BaseModel, Field


class EvidenceSufficiency(BaseModel):
    supporting_count: int = Field(ge=0)
    challenging_count: int = Field(ge=0)
    verified_supporting_count: int = Field(ge=0)
    source_domain_count: int = Field(ge=0)
    score: float = Field(ge=0, le=1)
    sufficient: bool
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
