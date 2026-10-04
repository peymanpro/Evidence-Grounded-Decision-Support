from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.config.settings import get_settings
from wealthbrain.infrastructure.models import DecisionRecord
from wealthbrain.modules.decisions.contracts import (
    AlternativeCreate,
    AlternativeResponse,
    AuditEventResponse,
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
from wealthbrain.modules.evidence.service import assess_sufficiency
from wealthbrain.modules.knowledge.contracts import HistoricalCaseSearchResult
from wealthbrain.modules.knowledge.service import KnowledgeService
from wealthbrain.modules.research.contracts import (
    ResearchExecutionRequest,
    ResearchQuestion,
    ResearchRun,
)
from wealthbrain.modules.research.factory import (
    create_research_provider,
    create_source_fetcher,
)
from wealthbrain.modules.research.repository import ResearchRunRepository
from wealthbrain.modules.research.service import ResearchService


class DecisionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = DecisionRepository(session)

    async def create(self, payload: DecisionCreate) -> DecisionResponse:
        record = await self._repo.create_decision(payload)
        await self._repo.add_audit_event(record.id, "decision_created")
        await self._session.commit()
        return DecisionResponse.model_validate(record)

    async def get(self, decision_id: UUID) -> DecisionResponse:
        return DecisionResponse.model_validate(await self._require(decision_id))

    async def add_alternative(
        self, decision_id: UUID, payload: AlternativeCreate
    ) -> AlternativeResponse:
        await self._require(decision_id)
        record = await self._repo.add_alternative(decision_id, payload)
        await self._repo.add_audit_event(
            decision_id,
            "alternative_added",
            {"alternative_id": str(record.id)},
        )
        await self._session.commit()
        return AlternativeResponse.model_validate(record)

    async def add_criterion(
        self, decision_id: UUID, payload: CriterionCreate
    ) -> CriterionResponse:
        await self._require(decision_id)
        record = await self._repo.add_criterion(decision_id, payload)
        await self._repo.add_audit_event(
            decision_id,
            "criterion_added",
            {"criterion_id": str(record.id)},
        )
        await self._session.commit()
        return CriterionResponse.model_validate(record)

    async def add_score(
        self, decision_id: UUID, payload: ScoreCreate
    ) -> dict[str, str]:
        await self._require(decision_id)
        try:
            await self._repo.add_score(decision_id, payload)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        await self._repo.add_audit_event(
            decision_id,
            "score_stored",
            {
                "criterion_id": str(payload.criterion_id),
                "alternative_id": str(payload.alternative_id),
            },
        )
        await self._session.commit()
        return {"status": "stored"}

    async def add_evidence(
        self, decision_id: UUID, payload: EvidenceCreate
    ) -> EvidenceResponse:
        await self._require(decision_id)
        record = await self._repo.add_evidence(decision_id, payload)
        await self._repo.add_audit_event(
            decision_id,
            "evidence_added",
            {"evidence_id": str(record.id)},
        )
        await self._session.commit()
        return EvidenceResponse.model_validate(record)

    async def add_risk(self, decision_id: UUID, payload: RiskCreate) -> RiskResponse:
        await self._require(decision_id)
        record = await self._repo.add_risk(decision_id, payload)
        await self._repo.add_audit_event(
            decision_id,
            "risk_added",
            {"risk_id": str(record.id)},
        )
        await self._session.commit()
        return RiskResponse.model_validate(record)

    async def add_journal_entry(
        self, decision_id: UUID, payload: JournalEntryCreate
    ) -> JournalEntryResponse:
        await self._require(decision_id)
        record = await self._repo.add_journal_entry(decision_id, payload)
        await self._repo.add_audit_event(
            decision_id,
            "journal_entry_added",
            {"journal_entry_id": str(record.id)},
        )
        await self._session.commit()
        return JournalEntryResponse.model_validate(record)

    async def run_research(
        self,
        decision_id: UUID,
        payload: ResearchExecutionRequest,
    ) -> ResearchRun:
        await self._require(decision_id)
        settings = get_settings()
        question = ResearchQuestion(
            question=payload.question,
            purpose=payload.purpose,
        )
        provider = create_research_provider(settings)
        fetcher = create_source_fetcher(settings)
        run = await ResearchService().run(
            question=question,
            provider=provider,
            fetcher=fetcher,
            max_results=min(payload.max_results, settings.research_max_results),
            domains=payload.domains,
        )
        record = await ResearchRunRepository(self._session).create(
            decision_id=decision_id,
            run=run,
            max_results=payload.max_results,
            domains=payload.domains,
        )
        run.id = str(record.id)
        await self._repo.add_audit_event(
            decision_id,
            "research_run_completed",
            {
                "research_run_id": str(record.id),
                "source_count": len(run.sources),
                "fetch_error_count": len(run.fetch_errors),
            },
        )
        await self._session.commit()
        return run

    async def related_cases(
        self,
        decision_id: UUID,
        limit: int = 5,
    ) -> list[HistoricalCaseSearchResult]:
        decision = await self._require(decision_id)
        return await KnowledgeService(self._session).related_to_decision(
            decision_type=decision.decision_type,
            query=decision.decision,
            limit=limit,
        )

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
        evidence_sufficiency = assess_sufficiency(evidence_models)
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
            evidence_sufficiency=evidence_sufficiency,
        )

    async def audit(self, decision_id: UUID) -> list[AuditEventResponse]:
        await self._require(decision_id)
        events = await self._repo.list_audit_events(decision_id)
        return [AuditEventResponse.model_validate(event) for event in events]

    async def _require(self, decision_id: UUID) -> DecisionRecord:
        record = await self._repo.get_decision(decision_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )
        return record
