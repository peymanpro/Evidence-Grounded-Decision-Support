from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.models import ConversationRecord, MessageRecord


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, title: str | None) -> ConversationRecord:
        record = ConversationRecord(title=title)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def get(self, conversation_id: UUID) -> ConversationRecord | None:
        return await self._session.get(ConversationRecord, conversation_id)

    async def list(self) -> list[ConversationRecord]:
        result = await self._session.scalars(
            select(ConversationRecord).order_by(ConversationRecord.updated_at.desc())
        )
        return list(result)

    async def update_title(self, record: ConversationRecord, title: str) -> ConversationRecord:
        record.title = title
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def delete(self, record: ConversationRecord) -> None:
        await self._session.delete(record)

    async def add_message(self, conversation_id: UUID, role: str, content: str) -> MessageRecord:
        record = MessageRecord(conversation_id=conversation_id, role=role, content=content)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def list_messages(self, conversation_id: UUID) -> list[MessageRecord]:
        result = await self._session.scalars(
            select(MessageRecord)
            .where(MessageRecord.conversation_id == conversation_id)
            .order_by(MessageRecord.created_at.asc())
        )
        return list(result)
