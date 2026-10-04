from datetime import UTC, datetime
from uuid import uuid4

from wealthbrain.modules.advisors.ai_service import ModelAdvisorService
from wealthbrain.modules.ai.fake import FakeAIProvider
from wealthbrain.modules.decisions.contracts import (
    DecisionReport,
    DecisionResponse,
)
from wealthbrain.modules.evidence.service import assess_sufficiency
from wealthbrain.modules.safety.contracts import SafetyCheckRequest
from wealthbrain.modules.safety.service import SafetyPolicy


class StubDecisionService:
    async def report(self, decision_id: object) -> DecisionReport:
        now = datetime.now(UTC)
        decision = DecisionResponse(
            id=uuid4(),
            conversation_id=None,
            decision="Compare options",
            decision_type="career",
            capital_at_risk=None,
            time_horizon_months=12,
            status="open",
            created_at=now,
            updated_at=now,
        )
        from wealthbrain.modules.decisions.engine import (
            calculate_quantitative,
            calculate_risk,
            critique_decision,
            synthesize,
        )

        quantitative = calculate_quantitative([], [], {})
        risk_analysis = calculate_risk([])
        critique = critique_decision([], [], quantitative)
        return DecisionReport(
            decision=decision,
            alternatives=[],
            criteria=[],
            evidence=[],
            risks=[],
            score_count=0,
            quantitative=quantitative,
            risk_analysis=risk_analysis,
            critique=critique,
            synthesis=synthesize(
                decision.id,
                quantitative,
                [],
                risk_analysis,
                critique,
            ),
            evidence_sufficiency=assess_sufficiency([]),
        )


async def test_model_advisor_service_uses_provider_boundary() -> None:
    service = ModelAdvisorService(
        decision_service=StubDecisionService(),  # type: ignore[arg-type]
        provider=FakeAIProvider(response="Challenge the assumptions."),
    )

    response = await service.review(
        decision_id=uuid4(),
        role="challenge",
        max_tokens=200,
    )

    assert response.provider == "fake"
    assert response.content == "Challenge the assumptions."
    assert response.human_review_required is True


async def test_safety_policy_blocks_recommendation_without_sufficient_evidence() -> None:
    report = await StubDecisionService().report(uuid4())
    result = SafetyPolicy().check(
        report,
        SafetyCheckRequest(
            intent="recommendation",
            acknowledgement=True,
        ),
    )

    assert result.allowed is False
    assert result.human_review_required is True
    assert result.reasons


async def test_safety_policy_allows_analysis_but_keeps_human_review() -> None:
    report = await StubDecisionService().report(uuid4())
    result = SafetyPolicy().check(
        report,
        SafetyCheckRequest(intent="analysis"),
    )

    assert result.allowed is True
    assert result.human_review_required is True


async def test_safety_policy_denies_external_action() -> None:
    report = await StubDecisionService().report(uuid4())
    result = SafetyPolicy().check(
        report,
        SafetyCheckRequest(intent="external_action"),
    )

    assert result.allowed is False
    assert result.human_review_required is True
