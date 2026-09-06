from abc import ABC, abstractmethod

from wealthbrain.modules.ai.contracts import CompletionRequest, CompletionResponse


class AIProviderError(RuntimeError):
    """A provider failed in a way the application can safely handle."""


class AIProviderTimeoutError(AIProviderError):
    """A provider did not return within its configured time budget."""


class AIProvider(ABC):
    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Return a validated completion or raise a domain-specific provider error."""
