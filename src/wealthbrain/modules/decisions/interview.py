from pydantic import BaseModel, Field

from wealthbrain.modules.decisions.contracts import DecisionReport


class InterviewQuestion(BaseModel):
    key: str = Field(min_length=1, max_length=50)
    question: str = Field(min_length=1, max_length=1_000)
    rationale: str = Field(min_length=1, max_length=1_000)


def next_questions(report: DecisionReport) -> list[InterviewQuestion]:
    questions: list[InterviewQuestion] = []
    decision = report.decision

    if decision.capital_at_risk is None and decision.decision_type in {
        "investment",
        "purchase",
        "business",
        "capital_allocation",
    }:
        questions.append(
            InterviewQuestion(
                key="capital_at_risk",
                question="How much capital is actually at risk in this decision?",
                rationale="Capital exposure materially changes the required evidence and risk threshold.",
            )
        )

    if decision.time_horizon_months is None:
        questions.append(
            InterviewQuestion(
                key="time_horizon",
                question="What time horizon should be used when judging the outcome?",
                rationale="A decision cannot be evaluated consistently without a defined horizon.",
            )
        )

    if not report.alternatives:
        questions.append(
            InterviewQuestion(
                key="alternatives",
                question="What realistic alternatives should be compared with the current option?",
                rationale="A decision should be compared against credible alternatives rather than evaluated in isolation.",
            )
        )

    if not report.criteria:
        questions.append(
            InterviewQuestion(
                key="criteria",
                question="Which criteria matter most, and how should their relative weights be set?",
                rationale="Weighted criteria make the trade-offs explicit and auditable.",
            )
        )

    if report.alternatives and report.criteria:
        expected = len(report.alternatives) * len(report.criteria)
        if report.score_count < expected:
            questions.append(
                InterviewQuestion(
                    key="scores",
                    question="Which alternative/criterion scores are still missing?",
                    rationale="Incomplete scoring weakens the quantitative comparison and its confidence.",
                )
            )

    if not report.evidence:
        questions.append(
            InterviewQuestion(
                key="evidence",
                question="What evidence or source material supports or challenges the key assumptions?",
                rationale="Claims without inspectable evidence should not drive a high-confidence conclusion.",
            )
        )

    if not report.risks:
        questions.append(
            InterviewQuestion(
                key="risks",
                question="What could make the preferred option fail, and how would you mitigate it?",
                rationale="Explicit downside scenarios make risk visible before action.",
            )
        )

    return questions


def missing_questions(report: DecisionReport) -> list[str]:
    return [item.question for item in next_questions(report)]
