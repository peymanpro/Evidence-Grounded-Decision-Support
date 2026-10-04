from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import KnowledgeCaseRecord
from wealthbrain.modules.knowledge.contracts import (
    HistoricalCaseCreate,
    HistoricalCaseResponse,
    HistoricalCaseSearchResult,
)
from wealthbrain.modules.knowledge.repository import KnowledgeRepository


class KnowledgeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = KnowledgeRepository(session)

    async def create(self, payload: HistoricalCaseCreate) -> HistoricalCaseResponse:
        record = await self._repository.create(payload)
        await self._session.commit()
        return self._to_response(record)

    async def get(self, case_id: UUID) -> HistoricalCaseResponse:
        record = await self._repository.get(case_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historical case not found",
            )
        return self._to_response(record)

    async def search(
        self,
        query: str,
        decision_type: str | None,
        limit: int,
    ) -> list[HistoricalCaseSearchResult]:
        records = await self._repository.search(query, decision_type, limit)
        return [
            HistoricalCaseSearchResult(
                case=self._to_response(record),
                relevance=self._relevance(record, query),
            )
            for record in records
        ]

    @staticmethod
    def _to_response(record: KnowledgeCaseRecord) -> HistoricalCaseResponse:
        return HistoricalCaseResponse(
            id=str(record.id),
            title=record.title,
            summary=record.summary,
            decision_type=record.decision_type,
            alternatives=list(record.alternatives),
            outcome=record.outcome,
            lessons=list(record.lessons),
            source_url=record.source_url,
            source_publisher=record.source_publisher,
            is_synthetic=record.is_synthetic,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    def _relevance(record: KnowledgeCaseRecord, query: str) -> float:
        tokens = {token.lower() for token in query.split() if token.strip()}
        if not tokens:
            return 0.0
        text = " ".join(
            [record.title, record.summary, record.outcome]
        ).lower()
        matches = sum(token in text for token in tokens)
        return round(min(1.0, matches / len(tokens)), 6)
