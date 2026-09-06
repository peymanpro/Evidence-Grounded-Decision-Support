import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from wealthbrain.api.conversations import router as conversations_router
from wealthbrain.config.settings import get_settings
from wealthbrain.infrastructure.database import create_engine, create_session_factory

settings = get_settings()
engine: AsyncEngine = create_engine(settings)
session_factory: async_sessionmaker[AsyncSession] = create_session_factory(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="WealthBrain API",
    version="0.1.0",
    description="Decision intelligence for wealth and capital-allocation decisions.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)
app.include_router(conversations_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await asyncio.wait_for(connection.execute(text("SELECT 1")), timeout=2.0)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc
    return {"status": "ready"}
