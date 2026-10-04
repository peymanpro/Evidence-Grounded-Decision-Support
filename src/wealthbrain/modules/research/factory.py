from wealthbrain.config.settings import Settings
from wealthbrain.modules.research.providers import (
    HttpJsonSearchProvider,
    ResearchProvider,
    SourceFetcher,
    StaticResearchProvider,
)


def create_research_provider(settings: Settings) -> ResearchProvider:
    if settings.default_research_provider == "fake":
        return StaticResearchProvider([])
    if not settings.research_search_url:
        raise ValueError(
            "RESEARCH_SEARCH_URL is required when DEFAULT_RESEARCH_PROVIDER=http"
        )
    return HttpJsonSearchProvider(
        endpoint=settings.research_search_url,
        api_key=settings.research_api_key,
        timeout_seconds=settings.research_timeout_seconds,
        max_response_bytes=settings.research_max_response_bytes,
    )


from wealthbrain.modules.research.providers import HttpSourceFetcher


def create_source_fetcher(settings: Settings) -> SourceFetcher:
    return HttpSourceFetcher(
        timeout_seconds=settings.research_timeout_seconds,
        max_response_bytes=settings.research_max_response_bytes,
        user_agent=settings.research_user_agent,
    )
