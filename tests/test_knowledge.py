from wealthbrain.modules.knowledge.contracts import HistoricalCaseCreate
from wealthbrain.modules.knowledge.service import KnowledgeService


def test_historical_case_contract_defaults_to_synthetic() -> None:
    case = HistoricalCaseCreate(
        title="A case",
        summary="Compare options.",
        decision_type="career",
        outcome="Option A won.",
    )

    assert case.is_synthetic is True


def test_historical_case_relevance_is_deterministic() -> None:
    from wealthbrain.infrastructure.models import KnowledgeCaseRecord

    record = KnowledgeCaseRecord(
        title="Career transition",
        summary="Compare career and income options.",
        decision_type="career",
        alternatives=["A", "B"],
        outcome="Option A was selected.",
        lessons=["Time horizon mattered."],
        is_synthetic=True,
    )

    relevance = KnowledgeService._relevance(record, "career option")

    assert relevance == 1.0
