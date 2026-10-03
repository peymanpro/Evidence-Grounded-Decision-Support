from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import (
    AlternativeRecord,
    CriterionRecord,
    DecisionRecord,
    DecisionScoreRecord,
    EvidenceRecord,
    JournalEntryRecord,
    RiskRecord,
)
from wealthbrain.modules.decisions.contracts import (
    AlternativeCreate,
    CriterionCreate,
    DecisionCreate,
    EvidenceCreate,
    JournalEntryCreate,
    RiskCreate,
    ScoreCreate,
)


class DecisionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_decision(self, payload: DecisionCreate) -> DecisionRecord:
        record = DecisionRecord(
            conversation_id=payload.conversation_id,
            decision=payload.decision,
            decision_type=payload.decision_type,
            capital_at_risk=payload.capital_at_risk,
            time_horizon_months=payload.time_horizon_months,
            status="open",
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_decision(self, decision_id: UUID) -> DecisionRecord | None:
        return await self.session.get(DecisionRecord, decision_id)

    async def list_alternatives(self, decision_id: UUID) -> list[AlternativeRecord]:
        result = await self.session.scalars(
            select(AlternativeRecord)
            .where(AlternativeRecord.decision_id == decision_id)
            .order_by(AlternativeRecord.created_at.asc())
        )
        return list(result)

    async def add_alternative(
        self, decision_id: UUID, payload: AlternativeCreate
    ) -> AlternativeRecord:
        record = AlternativeRecord(decision_id=decision_id, **payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def list_criteria(self, decision_id: UUID) -> list[CriterionRecord]:
        result = await self.session.scalars(
            select(CriterionRecord)
            .where(CriterionRecord.decision_id == decision_id)
            .order_by(CriterionRecord.created_at.asc())
        )
        return list(result)

    async def add_criterion(self, decision_id: UUID, payload: CriterionCreate) -> CriterionRecord:
        record = CriterionRecord(decision_id=decision_id, **payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def list_evidence(self, decision_id: UUID) -> list[EvidenceRecord]:
        result = await self.session.scalars(
            select(EvidenceRecord)
            .where(EvidenceRecord.decision_id == decision_id)
            .order_by(EvidenceRecord.created_at.asc())
        )
        return list(result)

    async def add_evidence(self, decision_id: UUID, payload: EvidenceCreate) -> EvidenceRecord:
        record = EvidenceRecord(decision_id=decision_id, **payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def list_risks(self, decision_id: UUID) -> list[RiskRecord]:
        result = await self.session.scalars(
            select(RiskRecord)
            .where(RiskRecord.decision_id == decision_id)
            .order_by(RiskRecord.created_at.asc())
        )
        return list(result)

    async def add_risk(self, decision_id: UUID, payload: RiskCreate) -> RiskRecord:
        record = RiskRecord(
            decision_id=decision_id,
            risk_score=round(payload.probability * payload.impact, 6),
            **payload.model_dump(),
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def add_score(self, decision_id: UUID, payload: ScoreCreate) -> None:
        criterion = await self.session.get(CriterionRecord, payload.criterion_id)
        alternative = await self.session.get(AlternativeRecord, payload.alternative_id)
        if (
            criterion is None
            or alternative is None
            or criterion.decision_id != decision_id
            or alternative.decision_id != decision_id
        ):
            raise ValueError("Score references must belong to the decision.")
        from sqlalchemy import delete

        await self.session.execute(
            delete(DecisionScoreRecord).where(
                DecisionScoreRecord.decision_id == decision_id,
                DecisionScoreRecord.criterion_id == payload.criterion_id,
                DecisionScoreRecord.alternative_id == payload.alternative_id,
            )
        )
        record = DecisionScoreRecord(
            decision_id=decision_id,
            criterion_id=payload.criterion_id,
            alternative_id=payload.alternative_id,
            score=payload.score,
        )
        self.session.add(record)
        await self.session.flush()

    async def list_scores(self, decision_id: UUID) -> list[DecisionScoreRecord]:
        result = await self.session.scalars(
            select(DecisionScoreRecord).where(DecisionScoreRecord.decision_id == decision_id)
        )
        return list(result)

    async def add_journal_entry(
        self, decision_id: UUID, payload: JournalEntryCreate
    ) -> JournalEntryRecord:
        record = JournalEntryRecord(decision_id=decision_id, **payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record
