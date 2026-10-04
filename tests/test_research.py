from datetime import UTC, datetime
from hashlib import sha256

import httpx
import pytest

from wealthbrain.config.settings import Settings
from wealthbrain.modules.research.contracts import (
    ResearchQuestion,
    ResearchSearchRequest,
    ResearchSearchResult,
    SourceDocument,
)
from wealthbrain.modules.research.factory import (
    create_research_provider,
    create_source_fetcher,
)
from wealthbrain.modules.research.normalizer import normalize_source
from wealthbrain.modules.research.providers import (
    HttpJsonSearchProvider,
    HttpSourceFetcher,
    ResearchProviderError,
    SourceFetchError,
    StaticResearchProvider,
    StaticSourceFetcher,
    validate_external_url,
)
from wealthbrain.modules.research.service import ResearchService

PUBLIC_URL = "https://93.184.216.34/article"


def make_document(url: str = PUBLIC_URL) -> SourceDocument:
    content = "Example article"
    return SourceDocument(
        url=url,
        status_code=200,
        content_type="text/plain",
        content=content,
        content_sha256=sha256(content.encode()).hexdigest(),
        content_length_bytes=len(content.encode()),
        retrieved_at=datetime.now(UTC),
    )


def test_research_search_request_has_bounded_results() -> None:
    request = ResearchSearchRequest(query="test", max_results=3)
    assert request.max_results == 3


def test_validate_external_url_blocks_local_addresses() -> None:
    for url in (
        "http://localhost:8000/secret",
        "http://127.0.0.1:8000/secret",
        "http://10.0.0.1/secret",
        "http://[::1]:8000/secret",
    ):
        with pytest.raises(SourceFetchError):
            validate_external_url(url)


def test_validate_external_url_rejects_unsafe_schemes_and_credentials() -> None:
    with pytest.raises(SourceFetchError):
        validate_external_url("file:///etc/passwd")
    with pytest.raises(SourceFetchError):
        validate_external_url("https://user:pass@example.com/private")


def test_validate_external_url_removes_fragment_from_public_url() -> None:
    assert validate_external_url(f"{PUBLIC_URL}#fragment") == PUBLIC_URL


def test_validate_external_url_blocks_private_dns_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_getaddrinfo(*args: object, **kwargs: object) -> list[tuple]:
        return [
            (
                2,
                1,
                6,
                "",
                ("10.0.0.5", 443),
            )
        ]

    monkeypatch.setattr(
        "wealthbrain.modules.research.providers.socket.getaddrinfo",
        fake_getaddrinfo,
    )
    with pytest.raises(SourceFetchError):
        validate_external_url("https://example.test")


def test_normalize_html_source() -> None:
    raw = """
    <html>
      <head><title>Example &amp; Research</title><style>secret</style></head>
      <body><h1>Hello</h1><script>alert(1)</script><p>World</p></body>
    </html>
    """
    digest = sha256(raw.encode()).hexdigest()

    result = normalize_source(
        url=PUBLIC_URL,
        content=raw,
        content_type="text/html",
        content_sha256=digest,
        content_length_bytes=len(raw.encode()),
    )

    assert result.title == "Example & Research"
    assert result.content == "Example & Research Hello World"
    assert result.content_sha256 == digest


async def test_static_research_pipeline_returns_normalized_document() -> None:
    provider = StaticResearchProvider(
        [
            ResearchSearchResult(
                title="Example",
                url=PUBLIC_URL,
                snippet="A snippet",
                publisher="Example",
            )
        ]
    )
    fetcher = StaticSourceFetcher({PUBLIC_URL: make_document()})

    result = await ResearchService().run(
        ResearchQuestion(
            question="What happened?",
            purpose="Find relevant evidence.",
        ),
        provider,
        fetcher,
    )

    assert result.sources[0].content_sha256 == make_document().content_sha256
    assert result.documents[0].content == "Example article"
    assert result.fetch_errors == []


async def test_research_service_records_failed_fetch_without_losing_other_sources() -> None:
    good_url = PUBLIC_URL
    bad_url = "https://93.184.216.35/blocked"
    provider = StaticResearchProvider(
        [
            ResearchSearchResult(title="Good", url=good_url),
            ResearchSearchResult(title="Bad", url=bad_url),
        ]
    )
    fetcher = StaticSourceFetcher({good_url: make_document(good_url)})

    result = await ResearchService().run(
        ResearchQuestion(question="Compare", purpose="Research"),
        provider,
        fetcher,
    )

    assert len(result.sources) == 1
    assert len(result.documents) == 1
    assert len(result.fetch_errors) == 1


async def test_http_search_provider_parses_results_and_forwards_request() -> None:
    seen: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("authorization")
        seen["body"] = request.content
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Result",
                        "url": PUBLIC_URL,
                        "snippet": "snippet",
                    }
                ]
            },
            request=request,
        )

    provider = HttpJsonSearchProvider(
        endpoint="https://search.example.test",
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )
    results = await provider.search(
        ResearchSearchRequest(
            query="test",
            max_results=1,
            domains=["example.com"],
        )
    )

    assert results[0].title == "Result"
    assert seen["authorization"] == "Bearer secret"
    assert b'"domains":["example.com"]' in seen["body"]


async def test_http_search_provider_rejects_oversized_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"x" * 32,
            headers={"content-type": "application/json"},
            request=request,
        )

    provider = HttpJsonSearchProvider(
        endpoint="https://search.example.test",
        api_key=None,
        max_response_bytes=16,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ResearchProviderError, match="byte limit"):
        await provider.search(ResearchSearchRequest(query="test"))


async def test_http_source_fetcher_blocks_redirects() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            headers={"location": PUBLIC_URL},
            request=request,
        )

    fetcher = HttpSourceFetcher(transport=httpx.MockTransport(handler))

    with pytest.raises(SourceFetchError, match="Redirect"):
        await fetcher.fetch(PUBLIC_URL)


async def test_http_source_fetcher_enforces_response_limit() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"x" * 32,
            headers={"content-type": "text/plain"},
            request=request,
        )

    fetcher = HttpSourceFetcher(
        max_response_bytes=16,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(SourceFetchError, match="byte limit"):
        await fetcher.fetch(PUBLIC_URL)


def test_research_factories_are_safe_by_default() -> None:
    settings = Settings(default_research_provider="fake")

    assert isinstance(create_research_provider(settings), StaticResearchProvider)
    assert isinstance(create_source_fetcher(settings), HttpSourceFetcher)
