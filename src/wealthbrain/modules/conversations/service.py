from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.modules.conversations.contracts import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)
from wealthbrain.modules.conversations.repository import ConversationRepository


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = ConversationRepository(session)

    async def create(self, payload: ConversationCreate) -> ConversationResponse:
        record = await self._repository.create(payload.title)
        await self._session.commit()
        return ConversationResponse.model_validate(record)

    async def list(self) -> list[ConversationResponse]:
        records = await self._repository.list_conversations()
        return [ConversationResponse.model_validate(record) for record in records]

    async def get(self, conversation_id: UUID) -> ConversationResponse:
        return ConversationResponse.model_validate(await self._require(conversation_id))

    async def update(
        self, conversation_id: UUID, payload: ConversationUpdate
    ) -> ConversationResponse:
        record = await self._require(conversation_id)
        record = await self._repository.update_title(record, payload.title)
        await self._session.commit()
        return ConversationResponse.model_validate(record)

    async def delete(self, conversation_id: UUID) -> None:
        record = await self._require(conversation_id)
        await self._repository.delete(record)
        await self._session.commit()

    async def add_message(
        self, conversation_id: UUID, payload: MessageCreate
    ) -> MessageResponse:
        await self._require(conversation_id)
        record = await self._repository.add_message(
            conversation_id, payload.role, payload.content
        )
        await self._session.commit()
        return MessageResponse.model_validate(record)

    async def list_messages(self, conversation_id: UUID) -> list[MessageResponse]:
        await self._require(conversation_id)
        records = await self._repository.list_messages(conversation_id)
        return [MessageResponse.model_validate(record) for record in records]

    async def _require(self, conversation_id: UUID):
        record = await self._repository.get(conversation_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        return record
