from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.database import session_dependency
from wealthbrain.modules.conversations.contracts import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)
from wealthbrain.modules.conversations.service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def get_session() -> AsyncIterator[AsyncSession]:
    from wealthbrain.main import session_factory

    async for session in session_dependency(session_factory):
        yield session


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ConversationService:
    return ConversationService(session)


Service = Annotated[ConversationService, Depends(get_service)]


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate, service: Service
) -> ConversationResponse:
    return await service.create(payload)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(service: Service) -> list[ConversationResponse]:
    return await service.list()


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: UUID, service: Service) -> ConversationResponse:
    return await service.get(conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID, payload: ConversationUpdate, service: Service
) -> ConversationResponse:
    return await service.update(conversation_id, payload)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: UUID, service: Service) -> Response:
    await service.delete(conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: UUID, payload: MessageCreate, service: Service
) -> MessageResponse:
    return await service.add_message(conversation_id, payload)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(conversation_id: UUID, service: Service) -> list[MessageResponse]:
    return await service.list_messages(conversation_id)
