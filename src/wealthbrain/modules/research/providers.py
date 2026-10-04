from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from hashlib import sha256
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlsplit

import httpx

from wealthbrain.modules.research.contracts import (
    ResearchSearchRequest,
    ResearchSearchResult,
    SourceDocument,
)


class ResearchProviderError(RuntimeError):
    """A research provider failed in a controlled way."""


class ResearchProviderTimeoutError(ResearchProviderError):
    """A research provider exceeded its configured time budget."""


class SourceFetchError(RuntimeError):
    """A source could not be fetched safely."""


class ResponseTooLargeError(RuntimeError):
    """A provider or source exceeded the configured byte limit."""


class ResearchProvider(ABC):
    @abstractmethod
    async def search(
        self, request: ResearchSearchRequest
    ) -> list[ResearchSearchResult]:
        """Search for candidate sources."""


class SourceFetcher(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> SourceDocument:
        """Fetch and return a bounded source document."""


def validate_external_url(url: str) -> str:
    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"}:
        raise SourceFetchError("Only HTTP and HTTPS URLs are allowed.")
    if parsed.username or parsed.password:
        raise SourceFetchError("URLs containing credentials are not allowed.")
    if not parsed.hostname:
        raise SourceFetchError("URL hostname is required.")
    if parsed.fragment:
        url = url.split("#", 1)[0]
        parsed = urlsplit(url)

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        raise SourceFetchError("Local hostnames are not allowed.")

    try:
        literal_ip = ip_address(hostname)
    except ValueError:
        literal_ip = None

    if literal_ip is not None and (
        literal_ip.is_private
        or literal_ip.is_loopback
        or literal_ip.is_link_local
        or literal_ip.is_multicast
        or literal_ip.is_reserved
        or literal_ip.is_unspecified
    ):
        raise SourceFetchError("Private, local, or reserved IP addresses are not allowed.")

    if literal_ip is None:
        try:
            resolved = socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
            )
        except OSError as exc:
            raise SourceFetchError("Could not resolve source hostname.") from exc
        addresses = {item[4][0] for item in resolved}
        for address in addresses:
            resolved_ip = ip_address(address)
            if (
                resolved_ip.is_private
                or resolved_ip.is_loopback
                or resolved_ip.is_link_local
                or resolved_ip.is_multicast
                or resolved_ip.is_reserved
                or resolved_ip.is_unspecified
            ):
                raise SourceFetchError(
                    "Source hostname resolves to a private, local, or reserved address."
                )

    return url


class HttpJsonSearchProvider(ResearchProvider):
    """Provider-neutral HTTP search adapter.

    The configured endpoint is expected to accept:
    {"query": "...", "max_results": N, "domains": ["..."]}
    and return:
    {"results": [{"title": "...", "url": "...", "snippet": "...", "publisher": "..."}]}
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str | None,
        timeout_seconds: float = 20.0,
        max_response_bytes: int = 1_000_000,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._max_response_bytes = max_response_bytes
        self._transport = transport

    async def search(
        self, request: ResearchSearchRequest
    ) -> list[ResearchSearchResult]:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = request.model_dump(mode="json")

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                async with client.stream(
                    "POST",
                    self._endpoint,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    body = await _bounded_response_bytes(
                        response, self._max_response_bytes
                    )
        except httpx.TimeoutException as exc:
            raise ResearchProviderTimeoutError("Research search timed out.") from exc
        except ResponseTooLargeError as exc:
            raise ResearchProviderError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ResearchProviderError("Research search request failed.") from exc

        try:
            decoded: Any = json.loads(body)
            raw_results = decoded["results"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ResearchProviderError("Research provider returned invalid JSON.") from exc
        if not isinstance(raw_results, list):
            raise ResearchProviderError("Research provider results must be a list.")

        return [
            ResearchSearchResult.model_validate(item)
            for item in raw_results[: request.max_results]
        ]


class HttpSourceFetcher(SourceFetcher):
    """Bounded source fetcher with redirects disabled.

    Redirects are intentionally handled as a later explicit hop so every URL
    can pass the same SSRF validation boundary.
    """

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        max_response_bytes: int = 2_000_000,
        user_agent: str = "WealthBrainResearch/0.2",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._timeout = timeout_seconds
        self._max_response_bytes = max_response_bytes
        self._user_agent = user_agent
        self._transport = transport

    async def fetch(self, url: str) -> SourceDocument:
        safe_url = validate_external_url(url)
        started = datetime.now(UTC)

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=False,
                headers={"User-Agent": self._user_agent},
                transport=self._transport,
            ) as client:
                async with client.stream("GET", safe_url) as response:
                    if 300 <= response.status_code < 400:
                        location = response.headers.get("location")
                        raise SourceFetchError(
                            "Redirect received but not followed automatically: "
                            f"{location or 'unknown'}"
                        )
                    response.raise_for_status()
                    content_type = (
                        response.headers.get(
                            "content-type", "application/octet-stream"
                        )
                        .split(";", 1)[0]
                        .strip()
                        .lower()
                    )
                    if content_type not in {
                        "text/html",
                        "text/plain",
                        "application/json",
                    }:
                        raise SourceFetchError(
                            f"Unsupported source content type: {content_type}"
                        )
                    content = await _bounded_response_bytes(
                        response, self._max_response_bytes
                    )
        except SourceFetchError:
            raise
        except httpx.TimeoutException as exc:
            raise SourceFetchError("Source fetch timed out.") from exc
        except ResponseTooLargeError as exc:
            raise SourceFetchError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise SourceFetchError("Source fetch failed.") from exc

        return SourceDocument(
            url=safe_url,
            status_code=response.status_code,
            content_type=content_type,
            content=content.decode(response.encoding or "utf-8", errors="replace"),
            content_sha256=sha256(content).hexdigest(),
            content_length_bytes=len(content),
            retrieved_at=started,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
        )


class StaticResearchProvider(ResearchProvider):
    """Deterministic provider for tests and offline development."""

    def __init__(self, results: Sequence[ResearchSearchResult]) -> None:
        self._results = list(results)

    async def search(
        self, request: ResearchSearchRequest
    ) -> list[ResearchSearchResult]:
        return self._results[: request.max_results]


class StaticSourceFetcher(SourceFetcher):
    def __init__(self, documents: dict[str, SourceDocument]) -> None:
        self._documents = documents

    async def fetch(self, url: str) -> SourceDocument:
        validate_external_url(url)
        document = self._documents.get(url)
        if document is None:
            raise SourceFetchError("No static source is configured for this URL.")
        return document


async def _bounded_response_bytes(
    response: httpx.Response, max_bytes: int
) -> bytes:
    header_length = response.headers.get("content-length")
    if header_length:
        try:
            if int(header_length) > max_bytes:
                raise ResponseTooLargeError("Response exceeds configured byte limit.")
        except ValueError:
            pass

    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > max_bytes:
            raise ResponseTooLargeError("Response exceeds configured byte limit.")
        chunks.append(chunk)
    return b"".join(chunks)
