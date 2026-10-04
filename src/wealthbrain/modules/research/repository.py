from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import ResearchRunRecord
from wealthbrain.modules.research.contracts import ResearchRun


class ResearchRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        decision_id: UUID,
        run: ResearchRun,
        max_results: int,
        domains: list[str],
    ) -> ResearchRunRecord:
        sources = [
            {
                "title": source.title,
                "url": str(source.url),
                "publisher": source.publisher,
                "retrieved_at": (
                    source.retrieved_at.isoformat()
                    if source.retrieved_at is not None
                    else None
                ),
                "status_code": source.status_code,
                "content_type": source.content_type,
                "content_sha256": source.content_sha256,
                "content_length_bytes": source.content_length_bytes,
                "snippet": source.snippet,
            }
            for source in run.sources
        ]
        record = ResearchRunRecord(
            decision_id=decision_id,
            question=run.question.question,
            purpose=run.question.purpose,
            provider=run.provider,
            max_results=max_results,
            domains=domains,
            sources=sources,
            fetch_errors=run.fetch_errors,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record
