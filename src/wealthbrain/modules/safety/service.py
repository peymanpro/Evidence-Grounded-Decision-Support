from wealthbrain.modules.decisions.contracts import DecisionReport
from wealthbrain.modules.safety.contracts import (
    SafetyCheckRequest,
    SafetyCheckResponse,
)


class SafetyPolicy:
    def check(
        self,
        report: DecisionReport,
        request: SafetyCheckRequest,
    ) -> SafetyCheckResponse:
        reasons: list[str] = []
        human_review_required = True

        if request.intent == "external_action":
            reasons.append(
                "WealthBrain does not autonomously execute consequential external actions."
            )
            return SafetyCheckResponse(
                intent=request.intent,
                allowed=False,
                human_review_required=True,
                reasons=reasons,
            )

        if request.intent == "recommendation":
            if not request.acknowledgement:
                reasons.append(
                    "Recommendation output requires explicit human acknowledgement."
                )
            if not report.evidence_sufficiency.sufficient:
                reasons.extend(report.evidence_sufficiency.blocking_issues)
            if report.risk_analysis.high_risk_count:
                reasons.append(
                    "High-risk items require human review before relying on a recommendation."
                )
            return SafetyCheckResponse(
                intent=request.intent,
                allowed=not reasons,
                human_review_required=True,
                reasons=reasons,
            )

        if request.intent == "analysis":
            reasons.extend(
                [
                    "Analysis remains decision support and may contain model or data errors.",
                    "Consequential actions remain under human control.",
                ]
            )
            return SafetyCheckResponse(
                intent=request.intent,
                allowed=True,
                human_review_required=human_review_required,
                reasons=reasons,
            )

        reasons.append("Unsupported safety intent.")
        return SafetyCheckResponse(
            intent=request.intent,
            allowed=False,
            human_review_required=True,
            reasons=reasons,
        )
