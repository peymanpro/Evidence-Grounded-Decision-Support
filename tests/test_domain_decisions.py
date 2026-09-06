from uuid import uuid4

import pytest
from pydantic import ValidationError

from wealthbrain.domain.decisions import DecisionContext, DecisionType


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
