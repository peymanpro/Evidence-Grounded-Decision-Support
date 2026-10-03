from collections.abc import Sequence
from uuid import UUID

from wealthbrain.modules.decisions.contracts import (
    AlternativeResponse,
    CritiqueResult,
    CriterionResponse,
    EvidenceResponse,
    QuantitativeAnalysis,
    RiskAnalysis,
    RiskResponse,
    SynthesisResult,
)


def calculate_quantitative(
    alternatives: Sequence[AlternativeResponse],
    criteria: Sequence[CriterionResponse],
    scores: dict[tuple[UUID, UUID], float],
) -> QuantitativeAnalysis:
    if not alternatives:
        return QuantitativeAnalysis(
            scores=[],
            preferred_alternative_id=None,
            preferred_alternative_name=None,
            sensitivity={},
            confidence=0.0,
        )

    total_weight = sum(criterion.weight for criterion in criteria)
    if total_weight <= 0:
        return QuantitativeAnalysis(
            scores=[
                {
                    "alternative_id": alternative.id,
                    "alternative_name": alternative.name,
                    "weighted_score": 0.0,
                    "normalized_score": 0.0,
                }
                for alternative in alternatives
            ],
            preferred_alternative_id=None,
            preferred_alternative_name=None,
            sensitivity={},
            confidence=0.0,
        )

    results = []
    for alternative in alternatives:
        weighted = 0.0
        for criterion in criteria:
            score = scores.get((alternative.id, criterion.id))
            if score is None:
                continue
            span = criterion.scale_max - criterion.scale_min
            normalized = (score - criterion.scale_min) / span if span else 0.0
            normalized = max(0.0, min(1.0, normalized))
            weighted += criterion.weight * normalized
        normalized_weighted = weighted / total_weight
        results.append(
            {
                "alternative_id": alternative.id,
                "alternative_name": alternative.name,
                "weighted_score": round(weighted, 6),
                "normalized_score": round(normalized_weighted, 6),
            }
        )

    results.sort(key=lambda item: item["normalized_score"], reverse=True)
    preferred = results[0] if results else None
    coverage = sum(
        criterion.weight
        for criterion in criteria
        if any((alternative.id, criterion.id) in scores for alternative in alternatives)
    )
    confidence = min(1.0, coverage / total_weight) if total_weight else 0.0

    sensitivity: dict[str, dict[str, float]] = {}
    for criterion in criteria:
        sensitivity[criterion.name] = {}
        for multiplier in (0.5, 1.5):
            weights = {
                item.id: (item.weight * multiplier if item.id == criterion.id else item.weight)
                for item in criteria
            }
            total = sum(weights.values())
            for alternative in alternatives:
                value = 0.0
                for item in criteria:
                    score = scores.get((alternative.id, item.id))
                    if score is None:
                        continue
                    span = item.scale_max - item.scale_min
                    normalized = (score - item.scale_min) / span if span else 0.0
                    value += weights[item.id] * max(0.0, min(1.0, normalized))
                sensitivity[criterion.name][f"{multiplier:.1f}:{alternative.name}"] = round(
                    value / total if total else 0.0, 6
                )

    return QuantitativeAnalysis(
        scores=results,
        preferred_alternative_id=preferred["alternative_id"] if preferred else None,
        preferred_alternative_name=preferred["alternative_name"] if preferred else None,
        sensitivity=sensitivity,
        confidence=round(confidence, 6),
    )


def calculate_risk(risks: Sequence[RiskResponse]) -> RiskAnalysis:
    ranked = sorted(risks, key=lambda risk: risk.risk_score, reverse=True)
    return RiskAnalysis(
        total_risk_score=round(sum(risk.risk_score for risk in risks), 6),
        high_risk_count=sum(risk.risk_score >= 6.0 for risk in risks),
        risks=[
            {
                "id": str(risk.id),
                "title": risk.title,
                "risk_score": round(risk.risk_score, 6),
                "probability": risk.probability,
                "impact": risk.impact,
                "mitigation": risk.mitigation,
            }
            for risk in ranked
        ],
    )


def critique_decision(
    evidence: Sequence[EvidenceResponse],
    risks: Sequence[RiskResponse],
    quantitative: QuantitativeAnalysis,
) -> CritiqueResult:
    strengths: list[str] = []
    concerns: list[str] = []
    missing: list[str] = []

    supporting = sum(item.supports for item in evidence)
    opposing = sum(not item.supports for item in evidence)

    if supporting:
        strengths.append(f"{supporting} supporting evidence item(s) are recorded.")
    else:
        missing.append("At least one decision-relevant supporting evidence item is missing.")

    if opposing:
        concerns.append(f"{opposing} evidence item(s) challenge the current decision framing.")

    if not risks:
        missing.append("No explicit risks have been recorded.")
    elif any(risk.risk_score >= 6 for risk in risks):
        concerns.append("At least one high-risk item requires explicit mitigation or human review.")

    if quantitative.confidence < 0.75:
        concerns.append("Quantitative analysis has incomplete criterion coverage.")

    if not quantitative.scores:
        missing.append("No alternatives have been quantitatively compared.")

    return CritiqueResult(
        strengths=strengths,
        concerns=concerns,
        missing_information=missing,
        human_review_required=bool(concerns or missing),
    )


def synthesize(
    decision_id: UUID,
    quantitative: QuantitativeAnalysis,
    evidence: Sequence[EvidenceResponse],
    risk_analysis: RiskAnalysis,
    critique: CritiqueResult,
) -> SynthesisResult:
    evidence_summary = [
        f"{item.title}: {'supports' if item.supports else 'challenges'} — {item.claim}"
        for item in evidence
    ]
    quantitative_summary = []
    if quantitative.preferred_alternative_name:
        quantitative_summary.append(
            f"Highest weighted alternative: {quantitative.preferred_alternative_name}."
        )
    quantitative_summary.append(
        f"Quantitative coverage confidence: {quantitative.confidence:.0%}."
    )

    risk_summary = [
        f"{item['title']}: score {item['risk_score']:.2f}" for item in risk_analysis.risks
    ]
    uncertainty = list(critique.missing_information) + list(critique.concerns)
    next_steps = [
        "Review assumptions, evidence, and risks before acting.",
        "Add missing evidence or revise criteria where uncertainty materially affects the ranking.",
    ]
    return SynthesisResult(
        decision_id=decision_id,
        preferred_alternative=quantitative.preferred_alternative_name,
        evidence_summary=evidence_summary,
        quantitative_summary=quantitative_summary,
        risk_summary=risk_summary,
        uncertainty=uncertainty,
        next_steps=next_steps,
        human_review_required=True,
    )
