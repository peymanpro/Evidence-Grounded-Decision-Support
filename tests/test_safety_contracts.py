import pytest

from wealthbrain.modules.safety.contracts import SafetyCheckRequest, SafetyCheckResponse


def test_external_action_is_a_bounded_intent() -> None:
    response = SafetyCheckResponse(
        intent="external_action",
        allowed=False,
        human_review_required=True,
        reasons=["Not executable."],
    )

    assert response.allowed is False


def test_unsupported_safety_intent_is_rejected_by_validation() -> None:
    with pytest.raises(ValueError):
        SafetyCheckRequest(intent="invalid_intent")  # type: ignore[arg-type]
