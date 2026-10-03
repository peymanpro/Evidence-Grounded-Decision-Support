from wealthbrain.modules.decisions.contracts import DecisionReport
from wealthbrain.modules.advisors.contracts import AdvisorPanel, AdvisorView


class AdvisorService:
    def review(self, report: DecisionReport) -> AdvisorPanel:
        views = [
            AdvisorView(
                name="Evidence",
                focus="evidence quality and uncertainty",
                observations=[
                    f"{len(report.evidence)} evidence item(s) are attached to the decision.",
                    *report.critique.concerns,
                ],
                questions=report.critique.missing_information,
            ),
            AdvisorView(
                name="Quantitative",
                focus="criteria, scoring, and sensitivity",
                observations=[
                    f"Scoring coverage confidence is {report.quantitative.confidence:.0%}.",
                    (
                        f"Current highest weighted alternative: "
                        f"{report.quantitative.preferred_alternative_name or 'none'}."
                    ),
                ],
                questions=[
                    "Which criteria or weights are most uncertain?",
                    "Would a materially different weight change the preferred alternative?",
                ],
            ),
            AdvisorView(
                name="Risk",
                focus="downside exposure and mitigation",
                observations=[
                    f"{report.risk_analysis.high_risk_count} high-risk item(s) are recorded.",
                    f"Aggregate risk score: {report.risk_analysis.total_risk_score:.2f}.",
                ],
                questions=[
                    item["title"] + " — what is the concrete mitigation trigger?"
                    for item in report.risk_analysis.risks[:3]
                ],
            ),
            AdvisorView(
                name="Challenge",
                focus="alternative explanations and hidden assumptions",
                observations=[
                    "A preferred alternative is provisional while evidence and assumptions remain incomplete."
                ],
                questions=[
                    "What evidence would most strongly change the current conclusion?",
                    "What is the best credible argument for the leading alternative?"
                ],
            ),
        ]
        return AdvisorPanel(views=views)
