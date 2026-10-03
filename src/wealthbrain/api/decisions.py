from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.database import session_dependency
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
from wealthbrain.modules.advisors.service import AdvisorService
from wealthbrain.modules.decisions.interview import missing_questions
from wealthbrain.modules.decisions.service import DecisionService
from wealthbrain.modules.evaluation.service import DecisionEvaluationService

router = APIRouter(prefix="/decisions", tags=["decisions"])


async def get_session() -> AsyncIterator[AsyncSession]:
    from wealthbrain.main import session_factory

    async for session in session_dependency(session_factory):
        yield session


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> DecisionService:
    return DecisionService(session)


Service = Annotated[DecisionService, Depends(get_service)]


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(payload: DecisionCreate, service: Service) -> DecisionResponse:
    return await service.create(payload)


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(decision_id: UUID, service: Service) -> DecisionResponse:
    return await service.get(decision_id)


@router.post("/{decision_id}/alternatives", response_model=AlternativeResponse)
async def add_alternative(
    decision_id: UUID, payload: AlternativeCreate, service: Service
) -> AlternativeResponse:
    return await service.add_alternative(decision_id, payload)


@router.post("/{decision_id}/criteria", response_model=CriterionResponse)
async def add_criterion(
    decision_id: UUID, payload: CriterionCreate, service: Service
) -> CriterionResponse:
    return await service.add_criterion(decision_id, payload)


@router.post("/{decision_id}/scores", response_model=dict[str, str])
async def add_score(
    decision_id: UUID, payload: ScoreCreate, service: Service
) -> dict[str, str]:
    return await service.add_score(decision_id, payload)


@router.post("/{decision_id}/evidence", response_model=EvidenceResponse)
async def add_evidence(
    decision_id: UUID, payload: EvidenceCreate, service: Service
) -> EvidenceResponse:
    return await service.add_evidence(decision_id, payload)


@router.post("/{decision_id}/risks", response_model=RiskResponse)
async def add_risk(
    decision_id: UUID, payload: RiskCreate, service: Service
) -> RiskResponse:
    return await service.add_risk(decision_id, payload)


@router.post("/{decision_id}/journal", response_model=JournalEntryResponse)
async def add_journal_entry(
    decision_id: UUID, payload: JournalEntryCreate, service: Service
) -> JournalEntryResponse:
    return await service.add_journal_entry(decision_id, payload)


@router.get("/{decision_id}/report", response_model=DecisionReport)
async def get_report(decision_id: UUID, service: Service) -> DecisionReport:
    return await service.report(decision_id)


@router.get("/{decision_id}/questions", response_model=list[str])
async def get_missing_questions(decision_id: UUID, service: Service) -> list[str]:
    report = await service.report(decision_id)
    return missing_questions(report)


@router.get("/{decision_id}/advisors")
async def get_advisor_panel(decision_id: UUID, service: Service) -> dict:
    report = await service.report(decision_id)
    return AdvisorService().review(report).model_dump(mode="json")


@router.get("/{decision_id}/quality")
async def get_quality_report(decision_id: UUID, service: Service) -> dict:
    report = await service.report(decision_id)
    return DecisionEvaluationService().evaluate(report).model_dump(mode="json")
