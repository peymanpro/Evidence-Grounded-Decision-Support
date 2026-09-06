import asyncio

from wealthbrain.modules.ai.contracts import CompletionRequest, CompletionResponse
from wealthbrain.modules.ai.provider import AIProvider, AIProviderError


class FakeAIProvider(AIProvider):
    """Deterministic provider for tests and local development without credentials."""

    def __init__(self, response: str = "Test completion", delay_seconds: float = 0.0) -> None:
        self._response = response
        self._delay_seconds = delay_seconds

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if self._delay_seconds:
            await asyncio.sleep(self._delay_seconds)
        return CompletionResponse(
            content=self._response,
            provider="fake",
            model=request.model,
            input_tokens=0,
            output_tokens=0,
        )


class FailingAIProvider(AIProvider):
    def __init__(self, message: str = "Simulated provider failure") -> None:
        self._message = message

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        raise AIProviderError(self._message)
