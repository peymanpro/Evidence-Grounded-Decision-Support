from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from wealthbrain.infrastructure.database import session_dependency
from wealthbrain.modules.knowledge.contracts import (
    HistoricalCaseCreate,
    HistoricalCaseResponse,
    HistoricalCaseSearchRequest,
    HistoricalCaseSearchResult,
)
from wealthbrain.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/knowledge/cases", tags=["knowledge"])


async def get_session() -> AsyncIterator[AsyncSession]:
    from wealthbrain.main import session_factory

    async for session in session_dependency(session_factory):
        yield session


def get_service(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> KnowledgeService:
    return KnowledgeService(session)


Service = Annotated[KnowledgeService, Depends(get_service)]


@router.post("", response_model=HistoricalCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: HistoricalCaseCreate, service: Service
) -> HistoricalCaseResponse:
    return await service.create(payload)


@router.get("/{case_id}", response_model=HistoricalCaseResponse)
async def get_case(case_id: UUID, service: Service) -> HistoricalCaseResponse:
    return await service.get(case_id)


@router.post("/search", response_model=list[HistoricalCaseSearchResult])
async def search_cases(
    payload: HistoricalCaseSearchRequest, service: Service
) -> list[HistoricalCaseSearchResult]:
    return await service.search(
        payload.query,
        payload.decision_type,
        payload.limit,
    )
