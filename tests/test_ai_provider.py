import asyncio

import pytest

from wealthbrain.config.settings import Settings
from wealthbrain.modules.ai.contracts import CompletionRequest
from wealthbrain.modules.ai.factory import create_ai_provider
from wealthbrain.modules.ai.fake import FailingAIProvider, FakeAIProvider
from wealthbrain.modules.ai.provider import AIProviderError


def request() -> CompletionRequest:
    return CompletionRequest(
        system_prompt="Be concise", user_prompt="Help me decide", model="test-model"
    )


async def test_fake_provider_returns_validated_response() -> None:
    response = await FakeAIProvider(response="Structured answer").complete(request())

    assert response.content == "Structured answer"
    assert response.provider == "fake"
    assert response.model == "test-model"


async def test_fake_provider_is_cancellable() -> None:
    task = asyncio.create_task(FakeAIProvider(delay_seconds=60).complete(request()))
    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


async def test_failing_provider_raises_safe_error() -> None:
    with pytest.raises(AIProviderError, match="Simulated provider failure"):
        await FailingAIProvider().complete(request())


def test_factory_creates_fake_provider_without_credentials() -> None:
    assert isinstance(create_ai_provider(Settings(default_ai_provider="fake")), FakeAIProvider)


def test_factory_rejects_unconfigured_real_provider() -> None:
    with pytest.raises(ValueError, match="not enabled"):
        create_ai_provider(Settings(default_ai_provider="openai"))
