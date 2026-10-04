import pytest

from wealthbrain.modules.advisors.contracts import AdvisorResponse


def test_advisor_response_requires_human_review() -> None:
    response = AdvisorResponse(
        role="challenge",
        provider="fake",
        model="test",
        content="Question the leading conclusion.",
    )

    assert response.human_review_required is True


def test_advisor_role_is_bounded() -> None:
    with pytest.raises(ValueError):
        AdvisorResponse(
            role="trading",  # type: ignore[arg-type]
            provider="fake",
            model="test",
            content="Not allowed.",
        )
