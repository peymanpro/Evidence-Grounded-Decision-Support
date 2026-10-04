from collections.abc import Sequence
from datetime import UTC, datetime

from wealthbrain.modules.research.contracts import (
    NormalizedSource,
    ResearchFinding,
    ResearchPlan,
    ResearchQuestion,
    ResearchRun,
    ResearchSearchRequest,
    ResearchSource,
)
from wealthbrain.modules.research.normalizer import normalize_source
from wealthbrain.modules.research.providers import (
    ResearchProvider,
    SourceFetcher,
    SourceFetchError,
)


class ResearchService:
    """Coordinate bounded search and source retrieval.

    Claim extraction and evidence linking intentionally remain outside this
    service and belong to the Evidence phase.
    """

    def build_plan(
        self,
        decision_id: str,
        questions: Sequence[ResearchQuestion],
    ) -> ResearchPlan:
        return ResearchPlan(
            decision_id=decision_id,
            questions=list(questions),
            findings=[],
        )

    def attach_findings(
        self,
        plan: ResearchPlan,
        findings: Sequence[ResearchFinding],
    ) -> ResearchPlan:
        return plan.model_copy(update={"findings": list(findings)})

    async def run(
        self,
        question: ResearchQuestion,
        provider: ResearchProvider,
        fetcher: SourceFetcher,
        *,
        max_results: int = 5,
        domains: Sequence[str] = (),
    ) -> ResearchRun:
        started = datetime.now(UTC)
        search_results = await provider.search(
            ResearchSearchRequest(
                query=question.question,
                max_results=max_results,
                domains=list(domains),
            )
        )
        sources: list[ResearchSource] = []
        documents: list[NormalizedSource] = []
        fetch_errors: list[str] = []

        for result in search_results:
            try:
                document = await fetcher.fetch(str(result.url))
            except SourceFetchError as exc:
                fetch_errors.append(f"{result.url}: {exc}")
                continue

            normalized = normalize_source(
                url=str(document.url),
                content=document.content,
                content_type=document.content_type,
                content_sha256=document.content_sha256,
                content_length_bytes=document.content_length_bytes,
            )
            documents.append(normalized)
            sources.append(
                ResearchSource(
                    title=normalized.title or result.title,
                    url=normalized.url,
                    publisher=result.publisher,
                    retrieved_at=document.retrieved_at,
                    status_code=document.status_code,
                    content_type=document.content_type,
                    content_sha256=normalized.content_sha256,
                    content_length_bytes=normalized.content_length_bytes,
                    snippet=result.snippet,
                )
            )

        return ResearchRun(
            question=question,
            provider=provider.__class__.__name__,
            started_at=started,
            completed_at=datetime.now(UTC),
            sources=sources,
            documents=documents,
            fetch_errors=fetch_errors,
        )
