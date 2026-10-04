from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.api.security import require_api_key
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
