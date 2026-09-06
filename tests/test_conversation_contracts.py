import pytest
from pydantic import ValidationError

from wealthbrain.modules.conversations.contracts import MessageCreate


def test_message_contract_normalizes_content() -> None:
    payload = MessageCreate(role="user", content="  تصمیم من چیست؟  ")

    assert payload.content == "تصمیم من چیست؟"


@pytest.mark.parametrize("role", ["tool", "", "USER"])
def test_message_contract_rejects_unknown_role(role: str) -> None:
    with pytest.raises(ValidationError):
        MessageCreate(role=role, content="hello")


def test_message_contract_rejects_blank_content() -> None:
    with pytest.raises(ValidationError):
        MessageCreate(role="user", content="\n  ")
