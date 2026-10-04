from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.config.settings import get_settings
from wealthbrain.infrastructure.database import session_dependency
from wealthbrain.modules.advisors.ai_service import ModelAdvisorService
from wealthbrain.modules.advisors.contracts import (
    AdvisorPanel,
    AdvisorRequest,
    AdvisorResponse,
)
from wealthbrain.modules.advisors.service import AdvisorService
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
from wealthbrain.modules.decisions.interview import (
    InterviewQuestion,
    missing_questions,
    next_questions,
)
from wealthbrain.modules.decisions.service import DecisionService
from wealthbrain.modules.evaluation.artifact import (
    EvaluationArtifact,
    build_evaluation_artifact,
)
from wealthbrain.modules.evaluation.contracts import DecisionQualityReport
from wealthbrain.modules.evaluation.service import DecisionEvaluationService
from wealthbrain.modules.evidence.contracts import EvidenceSufficiency
from wealthbrain.modules.knowledge.contracts import HistoricalCaseSearchResult
from wealthbrain.modules.orchestration.service import DecisionAIService
from wealthbrain.modules.research.contracts import (
    ResearchExecutionRequest,
    ResearchQuestion,
    ResearchRun,
)
from wealthbrain.modules.research.factory import (
    create_research_provider,
    create_source_fetcher,
)
from wealthbrain.modules.research.service import ResearchService
from wealthbrain.modules.safety.contracts import (
    SafetyCheckRequest,
    SafetyCheckResponse,
)
from wealthbrain.modules.safety.service import SafetyPolicy

router = APIRouter(prefix="/decisions", tags=["decisions"])


async def get_session() -> AsyncIterator[AsyncSession]:
    from wealthbrain.main import session_factory

    async for session in session_dependency(session_factory):
        yield session


def get_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DecisionService:
    return DecisionService(session)


Service = Annotated[DecisionService, Depends(get_service)]


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    payload: DecisionCreate,
    service: Service,
) -> DecisionResponse:
    return await service.create(payload)


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: UUID,
    service: Service,
) -> DecisionResponse:
    return await service.get(decision_id)


@router.post("/{decision_id}/alternatives", response_model=AlternativeResponse)
async def add_alternative(
    decision_id: UUID,
    payload: AlternativeCreate,
    service: Service,
) -> AlternativeResponse:
    return await service.add_alternative(decision_id, payload)


@router.post("/{decision_id}/criteria", response_model=CriterionResponse)
async def add_criterion(
    decision_id: UUID,
    payload: CriterionCreate,
    service: Service,
) -> CriterionResponse:
    return await service.add_criterion(decision_id, payload)


@router.post("/{decision_id}/scores", response_model=dict[str, str])
async def add_score(
    decision_id: UUID,
    payload: ScoreCreate,
    service: Service,
) -> dict[str, str]:
    return await service.add_score(decision_id, payload)


@router.post("/{decision_id}/evidence", response_model=EvidenceResponse)
async def add_evidence(
    decision_id: UUID,
    payload: EvidenceCreate,
    service: Service,
) -> EvidenceResponse:
    return await service.add_evidence(decision_id, payload)


@router.post("/{decision_id}/risks", response_model=RiskResponse)
async def add_risk(
    decision_id: UUID,
    payload: RiskCreate,
    service: Service,
) -> RiskResponse:
    return await service.add_risk(decision_id, payload)


@router.post("/{decision_id}/journal", response_model=JournalEntryResponse)
async def add_journal_entry(
    decision_id: UUID,
    payload: JournalEntryCreate,
    service: Service,
) -> JournalEntryResponse:
    return await service.add_journal_entry(decision_id, payload)


@router.get("/{decision_id}/audit", response_model=list[AuditEventResponse])
async def get_audit(
    decision_id: UUID,
    service: Service,
) -> list[AuditEventResponse]:
    return await service.audit(decision_id)


@router.get("/{decision_id}/report", response_model=DecisionReport)
async def get_report(
    decision_id: UUID,
    service: Service,
) -> DecisionReport:
    return await service.report(decision_id)


@router.get("/{decision_id}/questions", response_model=list[str])
async def get_missing_questions(
    decision_id: UUID,
    service: Service,
) -> list[str]:
    report = await service.report(decision_id)
    return missing_questions(report)


@router.get("/{decision_id}/next-question", response_model=InterviewQuestion | None)
async def get_next_question(
    decision_id: UUID,
    service: Service,
) -> InterviewQuestion | None:
    report = await service.report(decision_id)
    questions = next_questions(report)
    return questions[0] if questions else None


@router.get("/{decision_id}/advisors", response_model=AdvisorPanel)
async def get_advisor_panel(
    decision_id: UUID,
    service: Service,
) -> AdvisorPanel:
    report = await service.report(decision_id)
    return AdvisorService().review(report)


@router.post("/{decision_id}/ai-advisor", response_model=AdvisorResponse)
async def get_ai_advisor(
    decision_id: UUID,
    payload: AdvisorRequest,
    service: Service,
) -> AdvisorResponse:
    return await ModelAdvisorService(service).review(
        decision_id=decision_id,
        role=payload.role,
        max_tokens=payload.max_tokens,
    )


@router.get("/{decision_id}/quality", response_model=DecisionQualityReport)
async def get_quality_report(
    decision_id: UUID,
    service: Service,
) -> DecisionQualityReport:
    report = await service.report(decision_id)
    return DecisionEvaluationService().evaluate(report)


@router.get("/{decision_id}/evaluation-artifact", response_model=EvaluationArtifact)
async def get_evaluation_artifact(
    decision_id: UUID,
    service: Service,
) -> EvaluationArtifact:
    report = await service.report(decision_id)
    quality = DecisionEvaluationService().evaluate(report)
    return build_evaluation_artifact(report, quality)


@router.get(
    "/{decision_id}/evidence-sufficiency",
    response_model=EvidenceSufficiency,
)
async def get_evidence_sufficiency(
    decision_id: UUID,
    service: Service,
) -> EvidenceSufficiency:
    report = await service.report(decision_id)
    return report.evidence_sufficiency


@router.get("/{decision_id}/ai-critique")
async def get_ai_critique(
    decision_id: UUID,
    service: Service,
) -> dict[str, str]:
    critique = await DecisionAIService(service).critique(decision_id)
    return {"content": critique}


@router.get("/{decision_id}/research-plan")
async def get_research_plan(
    decision_id: UUID,
    service: Service,
) -> dict[str, object]:
    report = await service.report(decision_id)
    questions = missing_questions(report)
    plan = ResearchService().build_plan(
        str(decision_id),
        [
            ResearchQuestion(
                question=question,
                purpose="Fill a missing information or evidence gap.",
            )
            for question in questions
            if "evidence" in question.lower()
        ],
    )
    return plan.model_dump(mode="json")


@router.post("/{decision_id}/research", response_model=ResearchRun)
async def run_research(
    decision_id: UUID,
    payload: ResearchExecutionRequest,
    service: Service,
) -> ResearchRun:
    await service.get(decision_id)
    settings = get_settings()
    question = ResearchQuestion(
        question=payload.question,
        purpose=payload.purpose,
    )
    provider = create_research_provider(settings)
    fetcher = create_source_fetcher(settings)
    return await ResearchService().run(
        question=question,
        provider=provider,
        fetcher=fetcher,
        max_results=payload.max_results,
        domains=payload.domains,
    )


@router.get("/{decision_id}/related-cases")
async def get_related_cases(
    decision_id: UUID,
    service: Service,
) -> list[HistoricalCaseSearchResult]:
    return await service.related_cases(decision_id)


@router.post("/{decision_id}/safety-check", response_model=SafetyCheckResponse)
async def safety_check(
    decision_id: UUID,
    payload: SafetyCheckRequest,
    service: Service,
) -> SafetyCheckResponse:
    report = await service.report(decision_id)
    return SafetyPolicy().check(report, payload)
