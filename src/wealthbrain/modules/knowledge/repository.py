from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import KnowledgeCaseRecord
from wealthbrain.modules.knowledge.contracts import HistoricalCaseCreate


class KnowledgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payload: HistoricalCaseCreate) -> KnowledgeCaseRecord:
        values = payload.model_dump()
        if payload.source_url is not None:
            values["source_url"] = str(payload.source_url)
        record = KnowledgeCaseRecord(**values)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def get(self, case_id: UUID) -> KnowledgeCaseRecord | None:
        return await self._session.get(KnowledgeCaseRecord, case_id)

    async def search(
        self,
        query: str,
        decision_type: str | None,
        limit: int,
    ) -> list[KnowledgeCaseRecord]:
        pattern = f"%{query.strip()}%"
        statement = select(KnowledgeCaseRecord).where(
            or_(
                KnowledgeCaseRecord.title.ilike(pattern),
                KnowledgeCaseRecord.summary.ilike(pattern),
                KnowledgeCaseRecord.outcome.ilike(pattern),
            )
        )
        if decision_type:
            statement = statement.where(
                KnowledgeCaseRecord.decision_type == decision_type
            )
        statement = statement.order_by(KnowledgeCaseRecord.updated_at.desc()).limit(limit)
        result = await self._session.scalars(statement)
        return list(result)
