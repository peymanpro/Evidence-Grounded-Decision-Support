from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from wealthbrain.modules.decisions.contracts import (
    DecisionReport,
    DecisionResponse,
)
from wealthbrain.modules.evaluation.artifact import build_evaluation_artifact
from wealthbrain.modules.evaluation.contracts import DecisionQualityReport
from wealthbrain.modules.evaluation.interop import (
    decision_id_from_artifact,
    evaluation_case_payload,
    to_evaluation_suite_payload,
)


def make_artifact() -> Any:
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
    report = DecisionReport(
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
            "quantitative_summary": [],
            "risk_summary": [],
            "uncertainty": [],
            "next_steps": [],
            "human_review_required": True,
        },
    )
    quality = DecisionQualityReport(
        overall_score=0.0,
        checks=[],
        blocking_issues=["No evidence."],
    )
    return build_evaluation_artifact(report, quality)


def test_interop_payload_matches_evaluation_suite_shape() -> None:
    artifact = make_artifact()
    payload = to_evaluation_suite_payload(artifact)

    assert payload["version"] == "wealthbrain-0.3"
    assert len(payload["cases"]) == 3
    assert all(
        {"id", "input", "expected", "metadata", "tags", "risk_category"}
        <= set(case)
        for case in payload["cases"]
    )
    assert payload["metadata"]["input_fingerprint"] == artifact.evaluation_input_sha256


def test_interop_exposes_stable_case_lookup() -> None:
    artifact = make_artifact()
    case = evaluation_case_payload(
        artifact,
        signal="human_review_boundary",
    )

    assert case["expected"]["human_review_required"] is True
    assert decision_id_from_artifact(artifact) == artifact.decision_id
