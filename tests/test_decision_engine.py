from datetime import UTC, datetime
from uuid import uuid4

from wealthbrain.modules.decisions.contracts import (
    AlternativeResponse,
    CriterionResponse,
    EvidenceResponse,
    RiskResponse,
)
from wealthbrain.modules.decisions.engine import (
    calculate_quantitative,
    calculate_risk,
    critique_decision,
    synthesize,
)


def test_quantitative_analysis_ranks_alternatives() -> None:
    decision_id = uuid4()
    alternative_a = AlternativeResponse(
        id=uuid4(), decision_id=decision_id, name="A", description=""
    )
    alternative_b = AlternativeResponse(
        id=uuid4(), decision_id=decision_id, name="B", description=""
    )
    criterion = CriterionResponse(
        id=uuid4(),
        decision_id=decision_id,
        name="Fit",
        weight=1.0,
        scale_min=0.0,
        scale_max=10.0,
    )

    result = calculate_quantitative(
        [alternative_a, alternative_b],
        [criterion],
        {
            (alternative_a.id, criterion.id): 9.0,
            (alternative_b.id, criterion.id): 6.0,
        },
    )

    assert result.preferred_alternative_id == alternative_a.id
    assert result.scores[0].normalized_score > result.scores[1].normalized_score
    assert result.confidence == 1.0


def test_risk_analysis_orders_highest_score_first() -> None:
    decision_id = uuid4()
    now = datetime.now(UTC)
    low = RiskResponse(
        id=uuid4(),
        decision_id=decision_id,
        title="Low",
        probability=0.2,
        impact=2.0,
        risk_score=0.4,
        mitigation="",
        created_at=now,
    )
    high = RiskResponse(
        id=uuid4(),
        decision_id=decision_id,
        title="High",
        probability=0.8,
        impact=9.0,
        risk_score=7.2,
        mitigation="Reduce exposure",
        created_at=now,
    )

    result = calculate_risk([low, high])

    assert result.risks[0]["title"] == "High"
    assert result.high_risk_count == 1


def test_critique_requires_review_when_evidence_is_missing() -> None:
    quantitative = calculate_quantitative([], [], {})
    critique = critique_decision([], [], quantitative)

    assert critique.human_review_required is True
    assert critique.missing_information


def test_synthesis_never_marks_human_review_as_optional() -> None:
    decision_id = uuid4()
    quantitative = calculate_quantitative([], [], {})
    risk_analysis = calculate_risk([])
    critique = critique_decision([], [], quantitative)

    result = synthesize(decision_id, quantitative, [], risk_analysis, critique)

    assert result.decision_id == decision_id
    assert result.human_review_required is True


def test_supporting_and_challenging_evidence_are_distinguished() -> None:
    decision_id = uuid4()
    now = datetime.now(UTC)
    evidence = [
        EvidenceResponse(
            id=uuid4(),
            decision_id=decision_id,
            title="Support",
            source_url="https://example.com/support",
            claim="Supports the assumption.",
            supports=True,
            confidence=0.8,
            created_at=now,
        ),
        EvidenceResponse(
            id=uuid4(),
            decision_id=decision_id,
            title="Challenge",
            source_url="https://example.com/challenge",
            claim="Challenges the assumption.",
            supports=False,
            confidence=0.9,
            created_at=now,
        ),
    ]

    critique = critique_decision(evidence, [], calculate_quantitative([], [], {}))

    assert any("supporting evidence" in item for item in critique.strengths)
    assert any("challenge" in item for item in critique.concerns)
