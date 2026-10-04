# WealthBrain

**WealthBrain is a private decision-intelligence application for structured, evidence-aware reasoning about wealth, capital allocation, career, business, and other high-consequence decisions.**

It is not a trading bot, autonomous money manager, generic chatbot, or replacement for professional financial, legal, tax, or investment advice.

## Current status

**Version:** 0.3.1  
**Repository:** Private  
**Architecture:** Modular monolith  
**Primary stack:** Python 3.12 · FastAPI · SQLAlchemy async · PostgreSQL · Alembic · Docker

The current release contains a working decision-intelligence core with deterministic analysis, adaptive interviewing, research/source retrieval boundaries, evidence provenance, historical cases, specialist perspectives, model-assisted critique, evaluation artifacts, executable safety checks, audit events, observability, and a basic production security boundary.

The project is still evolving. It should not be described as a validated financial-advisory product or as production-complete autonomous AI.

## What is implemented

### Decision workflow

A decision can be represented with:

- decision context and type;
- alternatives;
- weighted criteria;
- scores;
- evidence and provenance;
- risks and mitigations;
- journal entries;
- deterministic analysis;
- critique;
- structured synthesis;
- audit events.

The quantitative core is deterministic and reproducible. Model output is kept outside the core numerical calculations.

### Adaptive interview

The system inspects the current decision state and identifies missing information.

Current question priorities include:

- capital exposure for financially relevant decisions;
- time horizon;
- missing alternatives;
- missing criteria;
- incomplete score matrices;
- missing evidence;
- missing risks.

The API can return either the full question set or the single next question.

### Research engine

Research is provider-neutral.

Current boundaries include:

- typed research questions and execution requests;
- configurable HTTP search-provider adapter;
- deterministic static provider for tests;
- bounded source fetching;
- HTTP/HTTPS-only source URLs;
- rejection of credential-bearing URLs;
- rejection of local/private/reserved address targets;
- redirects disabled by default;
- bounded response bodies;
- supported text/HTML/JSON content types;
- source normalization;
- SHA-256 content hashes;
- retrieval timestamps and HTTP metadata;
- persisted research-run metadata.

The research layer deliberately does **not** invent claims. Claim extraction and evidence linking remain separate responsibilities.

### Evidence system

Evidence now carries both a claim and its provenance:

- source URL;
- publisher;
- retrieval time;
- status/content metadata;
- content hash;
- content length;
- optional excerpt/locator;
- quality state.

Quality states are:

`unverified`, `partially_verified`, `verified`, `challenged`.

A deterministic evidence-sufficiency check reports:

- supporting and challenging evidence counts;
- verified-supporting count;
- source-domain diversity;
- sufficiency score;
- blocking issues;
- warnings.

### Historical knowledge

The knowledge module stores structured historical decision cases with:

- title and summary;
- decision type;
- alternatives;
- outcome;
- lessons;
- optional source metadata;
- synthetic-data flag.

Cases can be searched deterministically and related to an existing decision by decision type and text.

### Specialist advisors

The project contains two advisor layers.

**Deterministic panel:** evidence, quantitative, risk, and challenge perspectives.

**Model-backed advisor:** the same bounded roles can be executed through the provider abstraction, with human review remaining mandatory.

### AI provider boundary

The core depends on a small provider contract:

```text
CompletionRequest
       ↓
    AIProvider
       ↓
CompletionResponse
```

Current implementations include:

- `FakeAIProvider`;
- `FailingAIProvider`;
- OpenAI-compatible HTTP adapter;
- provider-specific error and timeout boundaries.

No provider credential is stored in the repository.

### Evaluation

The evaluation layer provides:

- decision-quality checks;
- blocking issues;
- structured evaluation artifacts;
- canonical evaluation-input fingerprints.

The fingerprint lets a later regression system refer to the same decision/evaluation input without relying on timestamps.

### Safety

Safety is implemented as executable policy, not only documentation.

Current policy:

- analysis is allowed as decision support, with human review retained;
- recommendation output is blocked when acknowledgement is absent, evidence is insufficient, or high-risk items remain;
- consequential external action is always denied by this application boundary.

### Observability and security baseline

Current runtime protections include:

- request IDs;
- request duration logging;
- liveness/readiness separation;
- production API-key guard;
- Trusted Host validation;
- security response headers;
- fixed-window single-process rate limiting;
- outbound source URL validation;
- bounded network responses.

The rate limiter is intentionally documented as single-process. Distributed rate limiting, full identity management, and deeper production hardening remain future work.

## Architecture

```text
                         WealthBrain API
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   Conversations          Decisions          Knowledge
          │                   │
          └────────────┬──────┘
                       ↓
                Application Services
                       ↓
             Deterministic / Domain Logic
                       ↓
                    Repositories
                       ↓
                SQLAlchemy + PostgreSQL

Decision workflow
   ↓
Adaptive Interview
   ↓
Research + Source Retrieval
   ↓
Evidence + Provenance
   ↓
Quantitative + Risk Analysis
   ↓
Specialist Perspectives
   ↓
Critique
   ↓
Synthesis
   ↓
Evaluation / Safety / Audit

AI boundary
   Application
       ↓
    AIProvider
       ├── Fake provider
       └── OpenAI-compatible HTTP provider
```

The architecture deliberately avoids premature microservices. A component should become a separate service only when scale, isolation, ownership, or operational evidence justifies it.

## API surface

### Health

```text
GET  /health
GET  /health/ready
```

### Conversations

```text
POST   /conversations
GET    /conversations
GET    /conversations/{id}
PATCH  /conversations/{id}
DELETE /conversations/{id}

POST   /conversations/{id}/messages
GET    /conversations/{id}/messages
```

### Decisions

```text
POST /decisions
GET  /decisions/{id}

POST /decisions/{id}/alternatives
POST /decisions/{id}/criteria
POST /decisions/{id}/scores
POST /decisions/{id}/evidence
POST /decisions/{id}/risks
POST /decisions/{id}/journal

GET  /decisions/{id}/report
GET  /decisions/{id}/audit
GET  /decisions/{id}/questions
GET  /decisions/{id}/next-question
GET  /decisions/{id}/advisors
POST /decisions/{id}/ai-advisor
GET  /decisions/{id}/quality
GET  /decisions/{id}/evaluation-artifact
GET  /decisions/{id}/evaluation-suite
GET  /decisions/{id}/evidence-sufficiency
GET  /decisions/{id}/ai-critique
GET  /decisions/{id}/research-plan
POST /decisions/{id}/research
GET  /decisions/{id}/related-cases
POST /decisions/{id}/safety-check
```

### Historical knowledge

```text
POST /knowledge/cases
POST /knowledge/cases/search
GET  /knowledge/cases/{id}
```

Interactive OpenAPI documentation is available at `/docs` when the API is running.

## Repository structure

```text
wealth-brain/
├── alembic/
│   └── versions/
│       ├── 0001_conversations.py
│       ├── 0002_decision_workspace.py
│       ├── 0003_decision_audit_events.py
│       ├── 0004_evidence_provenance.py
│       ├── 0005_knowledge_cases.py
│       └── 0006_research_runs.py
├── src/
│   └── wealthbrain/
│       ├── api/
│       ├── config/
│       ├── domain/
│       ├── infrastructure/
│       ├── modules/
│       │   ├── advisors/
│       │   ├── ai/
│       │   ├── decisions/
│       │   ├── evaluation/
│       │   ├── evidence/
│       │   ├── knowledge/
│       │   ├── orchestration/
│       │   ├── research/
│       │   ├── safety/
│       │   └── conversations/
│       └── main.py
├── tests/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Database migrations

The current Alembic chain is:

```text
0001 conversations
   ↓
0002 decision workspace
   ↓
0003 audit events
   ↓
0004 evidence provenance
   ↓
0005 historical knowledge
   ↓
0006 research runs
```

Apply migrations with:

```powershell
uv run alembic upgrade head
```

## Configuration

Configuration is environment-driven.

Example development settings:

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://wealthbrain:wealthbrain@localhost:5432/wealthbrain

DEFAULT_AI_PROVIDER=fake
DEFAULT_AI_MODEL=wealthbrain-test
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=

DEFAULT_RESEARCH_PROVIDER=fake
RESEARCH_SEARCH_URL=
RESEARCH_API_KEY=
RESEARCH_TIMEOUT_SECONDS=20
RESEARCH_MAX_RESPONSE_BYTES=1000000
RESEARCH_MAX_RESULTS=5
RESEARCH_USER_AGENT=WealthBrainResearch/0.3.1

API_KEY=
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60

LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
TRUSTED_HOSTS=*
```

Production deployments must keep credentials outside source control and must configure the API key explicitly.

## Local development

Install dependencies:

```powershell
uv sync --all-groups
```

Run migrations:

```powershell
uv run alembic upgrade head
```

Start the API:

```powershell
uv run uvicorn wealthbrain.main:app --reload
```

Run checks:

```powershell
uv run ruff check .
uv run mypy
uv run pytest
```

Run the full container stack:

```powershell
docker compose up --build
```

## Testing and CI

The repository treats automated checks as evidence for implemented scope.

Current CI sequence:

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

The latest verified code checkpoint is:

`a09f93dece3242094e526256700841061ca20041` (GitHub Actions Run 252)

Its CI run completed successfully with:

- Ruff ✅
- mypy ✅
- pytest ✅
- Docker build ✅

Subsequent documentation-only changes do not change the runtime behavior described above.

## Open-source direction

The repository remains **private**.

It is structured for a possible future public release and already includes:

- MIT License;
- `CONTRIBUTING.md`;
- `SECURITY.md`;
- `CODE_OF_CONDUCT.md`;
- `docs/ARCHITECTURE.md`;
- `docs/SAFETY.md`;
- `docs/OPEN_SOURCE.md`;
- synthetic-data expectations.

Before making the repository public, the project still needs a final security/history review, public API review, dependency/license review, and confirmation that no private decision data exists in Git history.

## Roadmap

The original 25-phase roadmap is preserved in `Git-Projects-Phase/projects/WealthBrain.md`.

The next unfinished areas are centered on:

- stronger evaluation and regression integration;
- deeper safety enforcement;
- production hardening;
- final release-candidate verification.

The roadmap is not being replaced by this README.

## Design principles

**Decision-first:** reason about a bounded decision rather than silently turning every conversation into a permanent profile.

**Evidence before confidence:** insufficient evidence is a visible state.

**Deterministic where possible:** quantitative calculations, ranking, risk scoring, and sufficiency checks should be reproducible.

**AI as a component, not the system:** model calls sit behind explicit contracts.

**Human control:** consequential external actions remain outside the application's autonomous boundary.

**Auditable evolution:** decisions, research runs, and important changes should leave inspectable metadata.

**Conservative claims:** implemented code, measured behavior, and roadmap intent are kept separate.

## License

The project is licensed under the MIT License.

The repository is currently private. The license does not imply that the repository is already publicly available.
