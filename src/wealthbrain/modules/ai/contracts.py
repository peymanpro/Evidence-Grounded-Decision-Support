from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=20_000)
    user_prompt: str = Field(min_length=1, max_length=20_000)
    model: str = Field(min_length=1, max_length=200)
    max_tokens: int = Field(default=1_000, ge=1, le=8_000)


class CompletionResponse(BaseModel):
    content: str = Field(min_length=1)
    provider: str
    model: str
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
