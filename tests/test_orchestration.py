from uuid import uuid4

import pytest
from pydantic import ValidationError

from wealthbrain.domain.decisions import DecisionContext, DecisionType
from wealthbrain.modules.orchestration.contracts import (
    AdvisoryRequest,
    OrchestrationPlan,
    ResearchTrigger,
    WorkflowStage,
)
from wealthbrain.modules.orchestration.service import OrchestrationService


def request(
    *,
    decision_type: DecisionType = DecisionType.BUSINESS,
    capital_at_risk: float | None = None,
    time_horizon_months: int | None = None,
    questions_asked: int = 0,
    text: str = "Should I open a second location?",
) -> AdvisoryRequest:
    return AdvisoryRequest(
        context=DecisionContext(
            conversation_id=uuid4(),
            decision="Open a second location",
            decision_type=decision_type,
            capital_at_risk=capital_at_risk,
            time_horizon_months=time_horizon_months,
        ),
        request_text=text,
        questions_asked=questions_asked,
    )


def test_fully_specified_business_decision_skips_interview_and_research() -> None:
    plan = OrchestrationService().plan(
        request(capital_at_risk=50_000, time_horizon_months=36)
    )

    assert plan.stages == (
        WorkflowStage.QUANTITATIVE_ANALYSIS,
        WorkflowStage.RISK_ANALYSIS,
        WorkflowStage.CRITIQUE,
        WorkflowStage.SYNTHESIS,
    )
    assert plan.interview_question_budget == 0
    assert plan.research_triggers == ()


def test_current_iran_related_request_routes_to_research() -> None:
    plan = OrchestrationService().plan(
        request(
            capital_at_risk=10_000,
            time_horizon_months=12,
            text="Given current Iran market conditions, should I import equipment?",
        )
    )

    assert WorkflowStage.RESEARCH in plan.stages
    assert plan.research_triggers == (
        ResearchTrigger.CURRENT_INFORMATION,
        ResearchTrigger.MARKET_CONDITIONS,
        ResearchTrigger.IRAN_SPECIFIC,
    )


def test_multiword_research_signal_is_detected() -> None:
    plan = OrchestrationService().plan(
        request(
            capital_at_risk=10_000,
            time_horizon_months=12,
            text="How do market conditions affect this?",
        )
    )

    assert plan.research_triggers == (ResearchTrigger.MARKET_CONDITIONS,)


def test_interview_budget_is_bounded_by_three_questions() -> None:
    plan = OrchestrationService().plan(request(questions_asked=2))

    assert plan.interview_question_budget == 1
    assert WorkflowStage.INTERVIEW in plan.stages

    exhausted_plan = OrchestrationService().plan(request(questions_asked=3))
    assert exhausted_plan.interview_question_budget == 0
    assert WorkflowStage.INTERVIEW not in exhausted_plan.stages


def test_plan_requires_critique_immediately_before_synthesis() -> None:
    with pytest.raises(ValidationError, match="critique"):
        OrchestrationPlan(
            stages=(WorkflowStage.RISK_ANALYSIS, WorkflowStage.SYNTHESIS),
            interview_question_budget=0,
        )
