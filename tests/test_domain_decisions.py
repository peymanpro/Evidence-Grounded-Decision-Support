from uuid import uuid4

import pytest
from pydantic import ValidationError

from wealthbrain.domain.decisions import (
    Assumption,
    Calculation,
    DecisionContext,
    DecisionFrame,
    DecisionOption,
    DecisionType,
    Fact,
    Reasoning,
    Uncertainty,
)


def test_decision_context_normalizes_whitespace() -> None:
    context = DecisionContext(
        conversation_id=uuid4(),
        decision="  Buy   productive equipment ",
        decision_type=DecisionType.BUSINESS,
    )

    assert context.decision == "Buy productive equipment"
    assert context.decision_type is DecisionType.BUSINESS


def test_decision_context_rejects_blank_decision() -> None:
    with pytest.raises(ValidationError):
        DecisionContext(conversation_id=uuid4(), decision="   ")


def test_decision_context_rejects_negative_capital_at_risk() -> None:
    with pytest.raises(ValidationError):
        DecisionContext(conversation_id=uuid4(), decision="Invest", capital_at_risk=-1)


def test_decision_frame_keeps_analysis_categories_explicit_and_immutable() -> None:
    context = DecisionContext(
        conversation_id=uuid4(),
        decision="Invest in a new product line",
        decision_type=DecisionType.BUSINESS,
    )
    frame = DecisionFrame(
        context=context,
        options=(DecisionOption(name="Launch", decision_type=DecisionType.BUSINESS),),
        facts=(Fact(statement="The company has $50,000 in cash", source="cash ledger"),),
        assumptions=(Assumption(statement="Demand will grow next year"),),
        calculations=(
            Calculation(name="payback", formula="investment / annual cash flow", result=2.5),
        ),
        reasoning=(Reasoning(statement="A short payback can preserve liquidity"),),
        uncertainties=(Uncertainty(statement="Demand has not been independently validated"),),
    )

    assert frame.facts[0].source == "cash ledger"
    assert frame.assumptions[0].statement == "Demand will grow next year"
    assert frame.calculations[0].result == 2.5
    assert frame.reasoning[0].statement == "A short payback can preserve liquidity"
    assert frame.uncertainties[0].statement == "Demand has not been independently validated"
    with pytest.raises(ValidationError):
        frame.facts[0].statement = "Changed"  # type: ignore[misc]


def test_decision_frame_requires_non_empty_unique_options_in_the_same_category() -> None:
    context = DecisionContext(
        conversation_id=uuid4(), decision="Allocate capital", decision_type=DecisionType.INVESTMENT
    )

    with pytest.raises(ValidationError, match="at least 1 item"):
        DecisionFrame(context=context, options=())
    with pytest.raises(ValidationError, match="unique"):
        DecisionFrame(
            context=context,
            options=(
                DecisionOption(name="Index fund", decision_type=DecisionType.INVESTMENT),
                DecisionOption(name="  index   fund  ", decision_type=DecisionType.INVESTMENT),
            ),
        )
    with pytest.raises(ValidationError, match="categories"):
        DecisionFrame(
            context=context,
            options=(DecisionOption(name="Buy a car", decision_type=DecisionType.PURCHASE),),
        )
