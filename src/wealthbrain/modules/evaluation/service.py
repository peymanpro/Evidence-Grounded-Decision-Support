from wealthbrain.modules.decisions.contracts import DecisionReport
from wealthbrain.modules.evaluation.contracts import DecisionQualityReport, QualityCheck


class DecisionEvaluationService:
    def evaluate(self, report: DecisionReport) -> DecisionQualityReport:
        alternative_score = min(1.0, len(report.alternatives) / 2)
        criterion_score = min(1.0, len(report.criteria) / 2)
        evidence_score = min(1.0, len(report.evidence) / 3)
        risk_score = min(1.0, len(report.risks) / 2)
        score_coverage = (
            min(
                1.0,
                report.score_count / (len(report.alternatives) * len(report.criteria)),
            )
            if report.alternatives and report.criteria
            else 0.0
        )

        checks = [
            QualityCheck(
                name="alternatives",
                score=alternative_score,
                explanation="At least two plausible alternatives improve comparison quality.",
            ),
            QualityCheck(
                name="criteria",
                score=criterion_score,
                explanation="Multiple weighted criteria reduce dependence on one dimension.",
            ),
            QualityCheck(
                name="evidence",
                score=evidence_score,
                explanation="Recorded sources make claims inspectable.",
            ),
            QualityCheck(
                name="risk",
                score=risk_score,
                explanation="Explicit risks make downside assumptions visible.",
            ),
            QualityCheck(
                name="score_coverage",
                score=score_coverage,
                explanation=(
                    "Complete alternative-by-criterion scoring improves "
                    "quantitative completeness."
                ),
            ),
        ]

        overall = sum(item.score for item in checks) / len(checks)
        blocking: list[str] = []
        if not report.alternatives:
            blocking.append("No alternatives are recorded.")
        if not report.evidence:
            blocking.append("No evidence is recorded.")
        if not report.risks:
            blocking.append("No risks are recorded.")
        if report.score_count == 0:
            blocking.append("No quantitative scores are recorded.")

        return DecisionQualityReport(
            overall_score=round(overall, 6),
            checks=checks,
            blocking_issues=blocking,
        )
