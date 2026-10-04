from datetime import UTC, datetime
from uuid import uuid4

from wealthbrain.modules.decisions.contracts import DecisionReport, DecisionResponse
from wealthbrain.modules.evaluation.artifact import build_evaluation_artifact
from wealthbrain.modules.evaluation.contracts import DecisionQualityReport


def make_report() -> DecisionReport:
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
    return DecisionReport(
        decision=decision,
        alternatives=[],
        criteria=[],
        evidence=[],
        risks=[],
        score_count=0,
        quantitative={
            "scores": [],
            "preferred_alternative_id": None,
            "preferred_alternative_name": None,
            "sensitivity": {},
            "confidence": 0.0,
        },
        risk_analysis={
            "total_risk_score": 0.0,
            "high_risk_count": 0,
            "risks": [],
        },
        critique={
            "strengths": [],
            "concerns": [],
            "missing_information": [],
            "human_review_required": True,
        },
        synthesis={
            "decision_id": decision.id,
            "preferred_alternative": None,
            "evidence_summary": [],
            "quantitative_summary": ["No quantitative comparison."],
            "risk_summary": [],
            "uncertainty": ["Evidence is missing."],
            "next_steps": ["Gather evidence."],
            "human_review_required": True,
        },
    )


def test_evaluation_artifact_is_deterministic_in_shape() -> None:
    artifact = build_evaluation_artifact(
        make_report(),
        DecisionQualityReport(
            overall_score=0.0,
            checks=[],
            blocking_issues=["No evidence."],
        ),
    )

    assert artifact.artifact_version == "1.0"
    assert artifact.deterministic is True
    assert artifact.external_model_calls is False
    assert artifact.report.decision.id == artifact.decision_id
