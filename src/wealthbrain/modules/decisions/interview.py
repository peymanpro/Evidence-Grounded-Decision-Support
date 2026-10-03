from wealthbrain.modules.decisions.contracts import DecisionReport


def missing_questions(report: DecisionReport) -> list[str]:
    questions: list[str] = []
    decision = report.decision

    if decision.conversation_id is None:
        questions.append("Which conversation or context should this decision belong to?")

    if not report.alternatives:
        questions.append("What realistic alternatives should be compared with the current option?")

    if not report.criteria:
        questions.append("Which criteria matter most, and how should their relative weights be set?")

    if report.criteria and report.alternatives:
        expected = len(report.criteria) * len(report.alternatives)
        if report.score_count < expected:
            questions.append("Which alternative/criterion scores are still missing?")

    if not report.evidence:
        questions.append("What evidence or source material supports or challenges the key assumptions?")

    if not report.risks:
        questions.append("What could make the preferred option fail, and how would you mitigate it?")

    if decision.time_horizon_months is None:
        questions.append("What time horizon should be used when judging the outcome?")

    return questions
