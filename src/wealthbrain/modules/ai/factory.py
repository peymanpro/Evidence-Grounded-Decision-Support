from wealthbrain.config.settings import Settings
from wealthbrain.modules.ai.fake import FakeAIProvider
from wealthbrain.modules.ai.provider import AIProvider


def create_ai_provider(settings: Settings) -> AIProvider:
    """Create only configured, credential-free providers in the initial foundation."""
    if settings.default_ai_provider == "fake":
        return FakeAIProvider()
    raise ValueError(
        f"AI provider '{settings.default_ai_provider}' is not enabled; "
        "use the fake provider until real integration."
    )
