from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import DecisionRecord

from wealthbrain.modules.decisions.contracts import (
    AlternativeCreate,
    AlternativeResponse,
    CriterionCreate,
    CriterionResponse,
    DecisionCreate,
    DecisionReport,
    DecisionResponse,
    EvidenceCreate,
    EvidenceResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    RiskCreate,
    RiskResponse,
    ScoreCreate,
)
from wealthbrain.modules.decisions.engine import (
    calculate_quantitative,
    calculate_risk,
    critique_decision,
    synthesize,
)
from wealthbrain.modules.decisions.repository import DecisionRepository


class DecisionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = DecisionRepository(session)

    async def create(self, payload: DecisionCreate) -> DecisionResponse:
        record = await self._repo.create_decision(payload)
        await self._session.commit()
        return DecisionResponse.model_validate(record)

    async def get(self, decision_id: UUID) -> DecisionResponse:
        return DecisionResponse.model_validate(await self._require(decision_id))

    async def add_alternative(
        self, decision_id: UUID, payload: AlternativeCreate
    ) -> AlternativeResponse:
        await self._require(decision_id)
        record = await self._repo.add_alternative(decision_id, payload)
        await self._session.commit()
        return AlternativeResponse.model_validate(record)

    async def add_criterion(
        self, decision_id: UUID, payload: CriterionCreate
    ) -> CriterionResponse:
        await self._require(decision_id)
        record = await self._repo.add_criterion(decision_id, payload)
        await self._session.commit()
        return CriterionResponse.model_validate(record)

    async def add_score(self, decision_id: UUID, payload: ScoreCreate) -> dict[str, str]:
        await self._require(decision_id)
        try:
            await self._repo.add_score(decision_id, payload)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        await self._session.commit()
        return {"status": "stored"}

    async def add_evidence(
        self, decision_id: UUID, payload: EvidenceCreate
    ) -> EvidenceResponse:
        await self._require(decision_id)
        record = await self._repo.add_evidence(decision_id, payload)
        await self._session.commit()
        return EvidenceResponse.model_validate(record)

    async def add_risk(self, decision_id: UUID, payload: RiskCreate) -> RiskResponse:
        await self._require(decision_id)
        record = await self._repo.add_risk(decision_id, payload)
        await self._session.commit()
        return RiskResponse.model_validate(record)

    async def add_journal_entry(
        self, decision_id: UUID, payload: JournalEntryCreate
    ) -> JournalEntryResponse:
        await self._require(decision_id)
        record = await self._repo.add_journal_entry(decision_id, payload)
        await self._session.commit()
        return JournalEntryResponse.model_validate(record)

    async def report(self, decision_id: UUID) -> DecisionReport:
        decision = await self._require(decision_id)
        alternatives = await self._repo.list_alternatives(decision_id)
        criteria = await self._repo.list_criteria(decision_id)
        evidence = await self._repo.list_evidence(decision_id)
        risks = await self._repo.list_risks(decision_id)
        stored_scores = await self._repo.list_scores(decision_id)

        scores = {
            (item.alternative_id, item.criterion_id): item.score for item in stored_scores
        }
        alternative_models = [
            AlternativeResponse.model_validate(item) for item in alternatives
        ]
        criterion_models = [CriterionResponse.model_validate(item) for item in criteria]
        evidence_models = [EvidenceResponse.model_validate(item) for item in evidence]
        risk_models = [RiskResponse.model_validate(item) for item in risks]

        quantitative = calculate_quantitative(
            alternative_models, criterion_models, scores
        )
        risk_analysis = calculate_risk(risk_models)
        critique = critique_decision(evidence_models, risk_models, quantitative)
        synthesis = synthesize(
            decision.id, quantitative, evidence_models, risk_analysis, critique
        )

        return DecisionReport(
            decision=DecisionResponse.model_validate(decision),
            alternatives=alternative_models,
            criteria=criterion_models,
            evidence=evidence_models,
            risks=risk_models,
            score_count=len(stored_scores),
            quantitative=quantitative,
            risk_analysis=risk_analysis,
            critique=critique,
            synthesis=synthesis,
        )

    async def _require(self, decision_id: UUID) -> DecisionRecord:
        record = await self._repo.get_decision(decision_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
            )
        return record
