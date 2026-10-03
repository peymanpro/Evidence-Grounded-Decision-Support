from wealthbrain.config.settings import Settings
from wealthbrain.modules.ai.fake import FakeAIProvider
from wealthbrain.modules.ai.provider import AIProvider
from wealthbrain.modules.ai.real import OpenAICompatibleProvider


def create_ai_provider(settings: Settings) -> AIProvider:
    if settings.default_ai_provider == "fake":
        return FakeAIProvider()
    if settings.default_ai_provider == "openai":
        if not settings.ai_api_key:
            raise ValueError("AI_API_KEY is required when DEFAULT_AI_PROVIDER=openai")
        return OpenAICompatibleProvider(
            base_url=settings.ai_base_url,
            api_key=settings.ai_api_key,
            timeout_seconds=settings.ai_timeout_seconds,
        )
    raise ValueError(
        f"AI provider '{settings.default_ai_provider}' is not enabled; "
        "supported providers are fake and openai."
    )
