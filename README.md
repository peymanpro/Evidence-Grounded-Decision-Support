# WealthBrain

**WealthBrain is a private decision-intelligence application for reasoning about wealth, capital-allocation, and other high-consequence decisions.**

It is being developed as a long-lived personal system rather than as a public demo or a generic chatbot.

The intended product direction is:

```text
Decision
   ↓
Context
   ↓
Conversation
   ↓
Research & Evidence
   ↓
Quantitative / Risk Analysis
   ↓
Specialist Perspectives
   ↓
Critique
   ↓
Synthesis
   ↓
Decision Journal
   ↓
Evaluation & Improvement
```

The current repository is deliberately at the beginning of that journey. The implemented code is the **Phase 01 foundation**, not a completed wealth-advisory system.

## Why WealthBrain Exists

Many financial and strategic decisions cannot be reduced to a single prediction or a single model output.

A useful decision system needs to preserve the decision context, identify missing information, separate evidence from assumptions, compare alternatives, reason quantitatively where appropriate, surface risks and contradictions, and retain an auditable history of how a conclusion was reached.

WealthBrain is intended to become that kind of system.

Its long-term focus is therefore **decision intelligence**, not:

- a trading bot;
- an autonomous money manager;
- a generic conversational assistant;
- a collection of unrelated AI agents;
- a replacement for professional financial, legal, tax, or investment advice.

## Current Status

**Version:** `0.1.0`  
**Repository:** Private  
**Current phase:** Phase 01 — Project Foundation  
**Implementation state:** Foundation scaffold implemented; further phases are intentionally unfinished.

Phase 01 currently contains:

- FastAPI application structure;
- PostgreSQL persistence with SQLAlchemy 2.x;
- Alembic migrations;
- conversation and message persistence;
- a bounded decision-domain model;
- provider-neutral AI contracts;
- a deterministic fake AI provider for local development and tests;
- configuration loaded through Pydantic Settings;
- liveness and database-readiness health endpoints;
- Docker and Docker Compose support;
- CI checks for Ruff, mypy, pytest, and Docker build.

Real model integration, research, evidence, quantitative analysis, specialist advisors, critique, synthesis, evaluation, observability, and deployment are **not yet implemented** in the current release.

## Core Product Idea

The system is designed around a decision rather than around a user profile.

A decision is treated as a bounded object with its own:

- question;
- type;
- relevant context;
- financial exposure where applicable;
- time horizon;
- evidence;
- assumptions;
- alternatives;
- analyses;
- risks;
- critiques;
- final synthesis;
- subsequent outcome and lessons.

This is important because the same person can make many unrelated decisions under very different constraints. The system should reason from the context of the decision instead of silently turning every conversation into a permanent user profile.

## Architecture Direction

The project uses a modular architecture so that domain reasoning can evolve independently from infrastructure and external AI providers.

Current foundation:

```text
                 WealthBrain API
                       │
             ┌─────────┴─────────┐
             │                   │
      Conversations          Health
             │
       Application Service
             │
       Repository Layer
             │
        SQLAlchemy ORM
             │
         PostgreSQL

AI boundary
      Application → AIProvider
                       │
                 Fake Provider
              (current Phase 01)
```

The project is intentionally **provider-neutral** at the boundary. The current implementation exposes an `AIProvider` contract and a deterministic fake provider, while real provider integrations are reserved for later phases.

## Repository Structure

```text
wealth-brain/
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_conversations.py
├── src/
│   └── wealthbrain/
│       ├── api/
│       │   └── conversations.py
│       ├── config/
│       │   └── settings.py
│       ├── domain/
│       │   └── decisions.py
│       ├── infrastructure/
│       │   ├── database.py
│       │   └── models.py
│       ├── modules/
│       │   ├── ai/
│       │   └── conversations/
│       └── main.py
├── tests/
│   ├── test_ai_provider.py
│   ├── test_conversation_contracts.py
│   ├── test_domain_decisions.py
│   ├── test_health.py
│   └── test_settings.py
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Current API

The Phase 01 API provides the minimum persistence boundary needed for the later conversation system.

### Health

```http
GET /health
GET /health/ready
```

`/health` is a liveness check and does not require a working database connection.

`/health/ready` verifies database connectivity and returns HTTP 503 when the database is not ready.

### Conversations

```http
POST   /conversations
GET    /conversations
GET    /conversations/{conversation_id}
PATCH  /conversations/{conversation_id}
DELETE /conversations/{conversation_id}
```

### Messages

```http
POST /conversations/{conversation_id}/messages
GET  /conversations/{conversation_id}/messages
```

The current conversation API is intentionally simple. Authentication, authorization, streaming responses, tool calls, adaptive interviews, and AI-generated conversation turns belong to later phases.

## Domain Foundation

The first domain object is a bounded `DecisionContext`.

It currently captures:

- `conversation_id`
- decision text
- decision type
- capital at risk, when applicable
- time horizon in months

Supported decision types currently include:

```text
investment
purchase
business
career
capital_allocation
other
```

This is deliberately a small foundation. The domain model is expected to grow as later phases establish the actual decision concepts instead of prematurely designing the entire system.

## AI Provider Boundary

The current AI layer defines a provider contract:

```text
CompletionRequest
       ↓
     AIProvider
       ↓
CompletionResponse
```

The initial implementation includes:

- `FakeAIProvider` for deterministic local execution;
- `FailingAIProvider` for failure-path tests;
- provider-specific exception types;
- a provider factory that currently permits only the fake provider.

Real provider credentials are intentionally absent from the repository.

The planned architecture can later accommodate providers such as OpenAI, Anthropic, or Google without coupling the domain layer to a particular vendor.

## Persistence

The foundation uses:

- PostgreSQL 16;
- SQLAlchemy 2.x asynchronous APIs;
- `asyncpg`;
- Alembic migrations.

The initial schema contains:

- `conversations`
- `messages`

Messages use a foreign key to conversations with cascading deletion.

Schema creation is handled by Alembic rather than by application startup side effects.

## Configuration

Configuration is environment-driven through Pydantic Settings.

Example:

```env
APP_ENV=development
PORT=8000
DATABASE_URL=postgresql+asyncpg://wealthbrain:wealthbrain@db:5432/wealthbrain
DEFAULT_AI_PROVIDER=fake
DEFAULT_AI_MODEL=wealthbrain-test
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

Production configuration rejects the wildcard CORS origin.

Credentials and local environment files are not committed.

## Local Development

The project uses Python 3.12+ and the `uv` workflow.

### Install

```powershell
uv sync --all-groups
```

### Run the API

```powershell
uv run uvicorn wealthbrain.main:app --reload
```

### Run checks

```powershell
uv run ruff check .
uv run mypy
uv run pytest
```

### Run with Docker Compose

Create a local `.env` based on `.env.example`, then:

```powershell
docker compose up --build
```

The API is exposed on port `8000` by default.

To stop the stack:

```powershell
docker compose down
```

## Database Migrations

Apply migrations with:

```powershell
uv run alembic upgrade head
```

The current migration creates the conversations and messages tables.

## Testing Strategy

The current test suite focuses on foundation contracts and failure boundaries.

It covers:

- AI provider response validation;
- provider failure handling;
- cancellation behavior;
- provider factory boundaries;
- message input normalization and validation;
- decision-domain validation;
- liveness behavior without a database;
- CORS configuration safety.

As the project grows, the test strategy is expected to expand to domain invariants, workflow behavior, research/evidence correctness, quantitative calculations, model-provider behavior, safety rules, evaluation, persistence boundaries, and end-to-end decision flows.

## CI

GitHub Actions is configured to validate:

```text
uv sync
   ↓
Ruff
   ↓
mypy
   ↓
pytest
   ↓
Docker build
```

The repository treats passing checks as evidence for the implemented scope only; CI success does not imply that unfinished product phases exist.

## Product Roadmap

The roadmap is intentionally broader than the current implementation.

### Phase 01 — Project Foundation
Core service, persistence, configuration, provider boundary, health checks, tests, CI, and container scaffold.

### Phase 02 — Domain Core
Establish the durable domain model for decisions, alternatives, criteria, constraints, evidence, assumptions, and outcomes.

### Phase 03 — Persistence
Expand repositories and schema around the domain while preserving clean application boundaries.

### Phase 04 — Conversation System
Build the conversation lifecycle that will carry decision discovery and later reasoning workflows.

### Phase 05 — AI Provider Foundation
Introduce real model-provider adapters behind the existing provider boundary.

### Phase 06 — Basic Orchestrator
Coordinate deterministic application steps and AI calls without prematurely introducing complex autonomy.

### Phase 07 — Adaptive Interview
Enable the system to identify missing decision information and ask targeted follow-up questions.

### Phase 08 — Research Engine
Build the research workflow needed to gather information relevant to a decision.

### Phase 09 — Evidence System
Represent sources, claims, provenance, confidence, and evidence-to-conclusion relationships.

### Phase 10 — Wealth Knowledge / Historical Cases
Build structured domain knowledge and historical decision cases.

### Phase 11 — Specialist Advisors
Introduce specialist reasoning modules for distinct analytical perspectives.

### Phase 12 — Quantitative Engine
Add quantitative calculations and decision-support models where mathematics materially improves the decision.

### Phase 13 — Risk Analysis
Represent uncertainty, downside scenarios, sensitivities, and decision-relevant risk.

### Phase 14 — Critique Engine
Critically inspect intermediate reasoning, assumptions, evidence quality, and proposed conclusions.

### Phase 15 — Final Synthesis
Produce a structured synthesis that separates evidence, assumptions, uncertainty, alternatives, and recommendation-level conclusions.

### Phase 16 — Decision Journal
Preserve decisions, reasoning, outcomes, and later lessons for longitudinal learning.

### Phase 17 — Evaluation Framework
Measure system quality, regression, reliability, and decision-support behavior.

### Phase 18 — Safety / Guardrails
Establish explicit boundaries for high-consequence financial and personal decision contexts.

### Phase 19 — Observability
Add structured tracing, metrics, failure visibility, and operational diagnostics.

### Phase 20 — Production Hardening
Improve reliability, security, data integrity, configuration safety, and operational resilience.

### Phase 21 — End-to-End Workflows
Connect the major components into coherent complete decision workflows.

### Phase 22 — Real AI Integration
Move from deterministic scaffolding to real model-backed execution across the intended workflows.

### Phase 23 — Deployment
Establish a controlled deployment architecture suitable for the private application.

### Phase 24 — Documentation
Document architecture, decisions, operating procedures, limitations, and reproducibility.

### Phase 25 — Release Candidate
Verify the complete planned scope against the real implementation and produce a stable release candidate.

## Safety and Scope

WealthBrain operates in a domain where incorrect reasoning can have significant financial consequences.

The project therefore treats the following as design requirements rather than optional polish:

- clear evidence provenance;
- explicit uncertainty;
- separation of facts from assumptions;
- visible failure and insufficiency states;
- reproducible quantitative calculations;
- auditable decision history;
- human control over consequential actions;
- resistance to unsupported certainty.

The system is not intended to autonomously move money, execute trades, or make irreversible financial decisions on its own.

## Design Principles

### Decision-first

The primary object is the decision and its context, not an ever-growing user profile.

### Evidence before confidence

A confident answer without sufficient evidence is a failure mode, not a success condition.

### Quantitative where useful

Mathematics and statistical analysis should be introduced when they improve decision quality, not merely to make the system look sophisticated.

### Modular reasoning

Research, quantitative analysis, specialist perspectives, critique, and synthesis should remain separable so that each can be tested and improved independently.

### Provider neutrality

The core application should depend on stable AI contracts rather than on one model vendor.

### Reproducibility

Important calculations and evaluations should be reproducible and inspectable.

### Conservative claims

A working prototype should not be described as a production financial adviser, autonomous agent, or validated investment system until the corresponding evidence exists.

## Current Boundary

At `0.1.0`, WealthBrain is a **foundation project**.

It has the infrastructure necessary to continue building the decision system, but it does not yet implement the distinctive intelligence described by the long-term roadmap.

That distinction is intentional: the repository should show the real state of the system rather than presenting an architectural vision as if it were already implemented.

## Planned End State

The long-term system can be summarized as:

```text
                 ┌───────────────────┐
                 │ Decision Context  │
                 └─────────┬─────────┘
                           ↓
                    Adaptive Interview
                           ↓
                  Research + Evidence
                    ↙          ↘
           Quantitative       Specialists
              Analysis          / Advisors
                    ↘          ↙
                         Risk
                           ↓
                       Critique
                           ↓
                       Synthesis
                           ↓
                    Decision Journal
                           ↓
                      Evaluation
                           ↓
                   System Improvement
```

The architecture will evolve through the roadmap; this diagram describes the intended direction, not the current implementation.

## Privacy

This is a **private project**.

The repository is intended for personal development and experimentation around the WealthBrain system. Real financial or personally sensitive information should not be committed to source control.

`*.env` files and local development data are excluded from version control.

## License

No public open-source licensing commitment is currently declared for this private repository.
