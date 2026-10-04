import asyncio

from fastapi import HTTPException

from wealthbrain.api.security import require_api_key
from wealthbrain.config.settings import Settings
from wealthbrain.security.rate_limit import RateLimiter


def test_rate_limiter_blocks_after_limit() -> None:
    async def run() -> list[bool]:
        limiter = RateLimiter(limit=2, window_seconds=60)
        return [
            await limiter.allow("client"),
            await limiter.allow("client"),
            await limiter.allow("client"),
        ]

    assert asyncio.run(run()) == [True, True, False]


def test_development_does_not_require_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "wealthbrain.api.security.get_settings",
        lambda: Settings(app_env="development"),
    )

    async def run() -> None:
        await require_api_key(None)

    asyncio.run(run())


def test_production_rejects_missing_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "wealthbrain.api.security.get_settings",
        lambda: Settings(
            app_env="production",
            api_key="expected",
        ),
    )

    async def run() -> None:
        try:
            await require_api_key(None)
        except HTTPException as exc:
            assert exc.status_code == 401
        else:
            raise AssertionError("Expected missing API key to be rejected.")

    asyncio.run(run())
