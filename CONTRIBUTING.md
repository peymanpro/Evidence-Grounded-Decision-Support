# Contributing to WealthBrain

Thanks for considering a contribution.

## Development principles

Keep changes small, testable, and aligned with the architecture. Prefer explicit domain contracts over hidden behavior and avoid introducing provider-specific dependencies into the core domain.

Before opening a pull request:

1. Run `uv sync --all-groups`.
2. Run `uv run ruff check .`.
3. Run `uv run mypy`.
4. Run `uv run pytest`.
5. Run `docker build .` when the Docker boundary is affected.

## AI/provider changes

Provider adapters must remain behind the `AIProvider` interface. Tests should use deterministic providers and must not require real credentials or external model calls.

## Data and security

Never commit credentials, private decision data, production database dumps, or real personal financial records.

Changes that could weaken data isolation, input validation, logging hygiene, or safety boundaries should include tests and documentation.

## Pull requests

Explain:

- what changed;
- why it changed;
- what was tested;
- any limitations or follow-up work.

Large feature branches should be decomposed when practical so that each change is reviewable.
