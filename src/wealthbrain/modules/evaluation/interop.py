"""Interoperability helpers for AI-Evaluation-Engineering.

The module intentionally uses plain JSON-compatible dictionaries instead of
importing the sibling repository. That keeps WealthBrain deployable on its own
while producing a contract that AI-Evaluation-Engineering can load directly.
"""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any
from uuid import UUID

from wealthbrain.modules.evaluation.artifact import EvaluationArtifact


def to_evaluation_suite_payload(
    artifact: EvaluationArtifact,
    *,
    suite_version: str = "wealthbrain-0.3",
) -> dict[str, Any]:
    report = artifact.report
    quality = artifact.quality

    cases: list[dict[str, Any]] = [
        {
            "id": f"{report.decision.id}:quality",
            "input": {
                "decision_id": str(report.decision.id),
                "evaluation_input_sha256": artifact.evaluation_input_sha256,
                "signal": "decision_quality",
            },
            "expected": {
                "human_review_required": True,
                "blocking_issue_count": len(quality.blocking_issues),
            },
            "metadata": {
                "source": "WealthBrain",
                "artifact_version": artifact.artifact_version,
            },
            "tags": ["wealthbrain", "decision-quality"],
            "risk_category": "decision-support",
        },
        {
            "id": f"{report.decision.id}:evidence",
            "input": {
                "decision_id": str(report.decision.id),
                "signal": "evidence_sufficiency",
            },
            "expected": {
                "sufficient": report.evidence_sufficiency.sufficient,
                "score": report.evidence_sufficiency.score,
            },
            "metadata": {
                "supporting_count": report.evidence_sufficiency.supporting_count,
                "verified_supporting_count": (
                    report.evidence_sufficiency.verified_supporting_count
                ),
            },
            "tags": ["wealthbrain", "evidence"],
            "risk_category": "evidence",
        },
        {
            "id": f"{report.decision.id}:safety",
            "input": {
                "decision_id": str(report.decision.id),
                "signal": "human_review_boundary",
            },
            "expected": {
                "human_review_required": True,
            },
            "metadata": {
                "external_model_calls": artifact.external_model_calls,
            },
            "tags": ["wealthbrain", "safety"],
            "risk_category": "safety",
        },
    ]

    payload = {
        "version": suite_version,
        "cases": cases,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    payload["metadata"] = {
        "artifact_sha256": sha256(canonical).hexdigest(),
        "decision_id": str(report.decision.id),
        "input_fingerprint": artifact.evaluation_input_sha256,
    }
    return payload


def evaluation_case_payload(
    artifact: EvaluationArtifact,
    *,
    signal: str,
) -> dict[str, Any]:
    suite = to_evaluation_suite_payload(artifact)
    cases = suite["cases"]
    if not isinstance(cases, list):
        raise TypeError("Evaluation suite cases must be a list.")
    for case in cases:
        if not isinstance(case, dict):
            continue
        case_input = case.get("input")
        if isinstance(case_input, dict) and case_input.get("signal") == signal:
            return case
    raise ValueError(f"Unknown WealthBrain evaluation signal: {signal}")


def decision_id_from_artifact(artifact: EvaluationArtifact) -> UUID:
    return artifact.decision_id
