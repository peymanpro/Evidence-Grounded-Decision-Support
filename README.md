# Evidence-Grounded Decision Support

[![CI](https://github.com/peymanpro/Evidence-Grounded-Decision-Support/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/peymanpro/Evidence-Grounded-Decision-Support/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/peymanpro/Evidence-Grounded-Decision-Support)](https://github.com/peymanpro/Evidence-Grounded-Decision-Support/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**An AI-assisted decision-support backend for turning consequential choices into structured, evidence-aware, and auditable decision workflows.**

Evidence-Grounded Decision Support combines deterministic quantitative analysis with bounded research retrieval, evidence provenance, specialist perspectives, model-assisted critique, evaluation artifacts, explicit safety policies, and audit events. It is designed for decisions involving career, business, wealth, capital allocation, and other areas where assumptions, uncertainty, and evidence quality matter.

> **Scope and safety:** This is a decision-support engineering project, not a trading bot, autonomous money manager, or validated financial-advisory product. It does not replace professional financial, investment, legal, or tax advice. Consequential external actions remain outside the application's autonomous boundary.

## Project status

| Item | Current status |
|---|---|
| Version | **0.3.1** |
| Architecture | Modular monolith |
| Runtime | Python 3.12 · FastAPI |
| Persistence | Async SQLAlchemy · PostgreSQL · Alembic |
| Delivery | Docker · GitHub Actions |
| License | MIT |

The repository contains a working backend and test suite, but the application is still evolving. A passing CI run is evidence that the configured checks pass; it is not proof of financial correctness, real-world evidence truth, or complete production readiness.

## Why this project

Consequential decisions are not just text-generation problems. A useful system needs to represent the choice explicitly, reveal missing information, separate calculations from model output, track where evidence came from, and prevent low-confidence analysis from silently becoming an authoritative recommendation.

This project puts those boundaries into the software:

- **Explicit decision model:** alternatives, weighted criteria, scores, evidence, risks, mitigations, and decision-journal entries are represented as structured data.
- **Reproducible quantitative core:** deterministic decision and risk analysis is kept separate from model-generated content.
- **Evidence with provenance:** sources, retrieval metadata, content hashes, excerpts, and evidence-quality states remain inspectable.
- **Adaptive information gathering:** the API identifies important gaps in a decision and can ask for the next missing piece of information.
- **Provider-neutral AI and research:** external providers sit behind explicit interfaces rather than being coupled to the core domain logic.
- **Evaluation and safety boundaries:** quality checks, evaluation artifacts, acknowledgement requirements, blocking issues, and audit events are first-class parts of the workflow.
- **Human control:** AI assists analysis; it does not autonomously execute consequential external actions.

## Decision lifecycle

The modules support a structured workflow rather than a single unconstrained prompt.

~~~text
Decision context and alternatives
              |
              v
     Adaptive interview
              |
              v
   Research and source retrieval
              |
              v
     Evidence + provenance
              |
              v
 Quantitative and risk analysis
              |
              v
 Specialist perspectives and critique
              |
              v
       Structured synthesis
              |
              v
     Evaluation and safety checks
              |
              v
     Report + audit trail
~~~

The exact stages depend on the decision state and the API operation. Research retrieval does not itself establish that a claim is true; evidence linking and quality assessment remain separate responsibilities.

## Implemented capabilities

### 1. Structured decision workspace

A decision can contain:

- decision context and type;
- competing alternatives;
- weighted criteria and score matrices;
- supporting or challenging evidence;
- risks and mitigations;
- journal entries and audit events.

The engine provides deterministic quantitative comparison, sensitivity analysis, risk scoring, critique, and structured synthesis. Model output does not replace the underlying numeric calculations.

### 2. Adaptive interview

The interview logic inspects the current decision state and identifies missing inputs. Current question priorities include:

- capital exposure where financially relevant;
- time horizon;
- missing alternatives or criteria;
- incomplete score matrices;
- absent evidence;
- missing risks.

The API can return the complete set of questions or only the next question, making the interview usable incrementally.

### 3. Bounded, provider-neutral research

The research layer defines typed research questions and execution requests, with a configurable HTTP search-provider adapter and a deterministic static provider for tests.

Source-fetching boundaries include:

- HTTP/HTTPS URLs only;
- rejection of credential-bearing URLs and local, private, or reserved address targets;
- redirects disabled by default;
- bounded response size and timeouts;
- supported text, HTML, and JSON content types;
- normalized source metadata, retrieval timestamps, HTTP metadata, and SHA-256 content hashes;
- persisted research-run metadata.

These controls reduce exposure to unsafe outbound requests; they do not remove the need for deployment-level network controls. The research layer deliberately does **not** invent claims or silently equate retrieved text with verified evidence.

### 4. Evidence provenance and sufficiency

Evidence records connect a claim with its available source context, including:

- source URL and publisher;
- retrieval time and status/content metadata;
- content hash and content length;
- optional excerpt or locator;
- evidence-quality state.

Current quality states are:

**unverified**, **partially_verified**, **verified**, and **challenged**.

A deterministic sufficiency check reports supporting and challenging evidence counts, verified-supporting count, source-domain diversity, a sufficiency score, blocking issues, and warnings. This is an explicit policy signal for the application—not an independent proof that a source or claim is true.

### 5. Historical decision knowledge

The knowledge module stores structured historical cases with a title, summary, decision type, alternatives, outcome, lessons, optional source metadata, and a synthetic-data flag. Cases can be searched deterministically and related to a decision using decision type and text.

### 6. Specialist perspectives

Two advisor layers are available:

- **Deterministic panel:** evidence, quantitative, risk, and challenge perspectives.
- **Model-backed advisors:** bounded versions of those roles through the AI provider abstraction, with human review retained.

These perspectives are aids for reviewing a decision, not independent expert certifications.

### 7. Explicit AI provider boundary

The application depends on a small provider contract:

~~~text
CompletionRequest
       |
       v
    AIProvider
       |
       v
CompletionResponse
~~~

Implementations include FakeAIProvider, FailingAIProvider, and an OpenAI-compatible HTTP adapter with timeout and provider-error boundaries. Tests can use deterministic providers without live model credentials. Provider credentials must be supplied through environment configuration, not committed to source control.

### 8. Evaluation artifacts

The evaluation module provides decision-quality checks, blocking issues, structured evaluation artifacts, and canonical evaluation-input fingerprints. Fingerprints let regression tooling identify equivalent decision/evaluation inputs without relying on timestamps.

The repository exposes evaluation artifacts and an evaluation-suite export endpoint so external regression workflows can consume structured results.

### 9. Executable safety policy

Safety constraints are enforced in application logic as well as documented:

- decision analysis can be returned with human review retained;
- recommendation output can be blocked when required acknowledgement is absent, evidence is insufficient, or high-risk items remain;
- consequential external action is denied by this application boundary.

These are application-level controls. A real deployment still requires an appropriate identity, authorization, data-isolation, and operational-security design.

### 10. Observability and security baseline

Implemented runtime protections include request IDs, request-duration logging, separate liveness/readiness checks, a production API-key guard, Trusted Host validation, security response headers, a fixed-window rate limiter, and constrained outbound source fetching.

The rate limiter is **single-process**, not distributed. Distributed throttling, full identity and access management, and deeper production hardening remain open work.

## Architecture

The application is a modular monolith. This keeps domain logic and deployment simple while preserving boundaries that can be tested independently.

~~~text
FastAPI
  |
  +-- Conversations
  +-- Decisions ---------------------------+
  +-- Historical knowledge                 |
                                           v
                                  Application services
                                           |
                       +-------------------+-------------------+
                       |                   |                   |
                Deterministic logic   Research / evidence   AI providers
                       |                   |                   |
                       +-------------------+-------------------+
                                           |
                                   Repositories / ORM
                                           |
                                     PostgreSQL
                                           |
                                  Alembic migrations

Cross-cutting boundaries:
evaluation · safety · audit · observability · API security
~~~

The project deliberately avoids premature microservices. A component should become a separate service only when scale, isolation, ownership, or operational evidence makes that separation worthwhile.

## API overview

Interactive OpenAPI documentation is available at **/docs** while the API is running.

### Health

~~~http
GET /health
GET /health/ready
~~~

### Conversations

~~~http
POST   /conversations
GET    /conversations
GET    /conversations/{id}
PATCH  /conversations/{id}
DELETE /conversations/{id}

POST   /conversations/{id}/messages
GET    /conversations/{id}/messages
~~~

### Decisions

~~~http
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
~~~

### Historical knowledge

~~~http
POST /knowledge/cases
POST /knowledge/cases/search
GET  /knowledge/cases/{id}
~~~

## Run locally

### Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Engine / Docker Desktop for the container stack
- PostgreSQL, either local or through Docker Compose

### Option A: Docker Compose

Start the container stack:

~~~powershell
docker compose up --build
~~~

Then open **/docs** on the API address configured by Docker Compose.

### Option B: Local Python environment

Install dependencies:

~~~powershell
uv sync --all-groups
~~~

Apply database migrations:

~~~powershell
uv run alembic upgrade head
~~~

Start the API:

~~~powershell
uv run uvicorn wealthbrain.main:app --reload
~~~

Run checks locally:

~~~powershell
uv run ruff check .
uv run mypy
uv run pytest
docker build .
~~~

The database must be reachable and DATABASE_URL must be set for database-backed operations. API routes and external-provider behavior should be exercised against a configured environment before deployment.

## Configuration

The application is configured through environment variables. The following values illustrate a **development-only** setup; adjust them to your environment.

~~~dotenv
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
RESEARCH_USER_AGENT=EvidenceGroundedDecisionSupportResearch/0.3.1

API_KEY=
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60

LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
TRUSTED_HOSTS=*
~~~

Do not use these example credentials or permissive host settings in production. Production deployments must set explicit secrets, trusted hosts, CORS origins, and API authentication configuration, and must keep credentials outside source control.

## Tests and continuous integration

GitHub Actions validates the project with the same core checks used before a release:

~~~text
Dependency installation
         |
         v
      Ruff lint
         |
         v
       mypy
         |
         v
      pytest
         |
         v
     Docker build
~~~

Tests use deterministic providers where possible and should not require real model credentials. A green pipeline demonstrates that the configured automated checks passed for that commit; it does not certify advice quality, source truth, or production security.

## Automated releases

The release workflow is version-driven and runs the validation checks before publishing a GitHub Release.

- **Automatic from main:** after a successful validation run, the workflow publishes the version declared in pyproject.toml if that version has not already been released.
- **Tag-triggered:** pushing a tag such as v0.3.2 runs validation and requires the tag version to match the package version in pyproject.toml.
- **Manual:** the workflow can also be started from GitHub Actions. An optional version input must match the project version.
- **Release notes:** GitHub generates release notes automatically. An already-published version is left unchanged.

To prepare a future release, update the version in pyproject.toml and add the corresponding entry to CHANGELOG.md, then merge the changes into main. The workflow will publish that version only after linting, typing, tests, and the Docker build succeed. Stable release tags use the vMAJOR.MINOR.PATCH format.

## Repository layout

~~~text
.
├── .github/workflows/
│   ├── ci.yml
│   └── release.yml
├── alembic/
│   └── versions/
├── src/wealthbrain/
│   ├── api/
│   ├── config/
│   ├── domain/
│   ├── infrastructure/
│   ├── security/
│   └── modules/
│       ├── advisors/
│       ├── ai/
│       ├── conversations/
│       ├── decisions/
│       ├── evaluation/
│       ├── evidence/
│       ├── knowledge/
│       ├── orchestration/
│       ├── research/
│       └── safety/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
~~~

Database schema changes are managed with Alembic. The migration history currently covers conversations, the decision workspace, audit events, evidence provenance, historical knowledge, and research-run metadata.

## Security and data handling

Do not commit API keys, production database dumps, private decision records, or real personal financial data. Use synthetic data in tests and examples. Treat external model and research providers as untrusted boundaries, and do not expose an unauthenticated deployment that contains sensitive decision information.

Before handling real users' sensitive data, review the Git history, dependency posture, authentication and authorization, tenant/data isolation, logging, backups, network controls, and incident response. If a credential is exposed, revoke or rotate it immediately; deleting the visible file alone is insufficient.

See [SECURITY.md](SECURITY.md) for the project's security policy.

## Roadmap

The original 25-phase roadmap is maintained separately in the Git-Projects-Phase workspace.

Remaining work is focused on stronger evaluation/regression integration, deeper safety enforcement, additional production hardening, and continued release-candidate verification. The roadmap is not replaced by this README.

## Related engineering projects

The following public repositories explore adjacent parts of the broader AI/software-engineering portfolio. They are **separate projects**, not runtime dependencies of this application.

| Project | Focus |
|---|---|
| [AI Evaluation Engineering](https://github.com/peymanpro/AI-Evaluation-Engineering) | Reusable graders, statistical comparisons, regression gates, and a dependency-free interoperability contract with this project's evaluation-suite export API |
| [Pretrained LLM Adaptation](https://github.com/peymanpro/Pretrained-LLM-Adaptation) | Reproducible LoRA/PEFT adaptation, held-out evaluation, and inference |
| [Evidence-Grounded RAG](https://github.com/peymanpro/Evidence-Grounded-RAG) | Retrieval, grounded generation, citation verification, and retrieval evaluation |
| [Production Agent Systems](https://github.com/peymanpro/Production-Agent-Systems) | Tool contracts, runtime policy, bounded retries, checkpoint/recovery, trace, and audit |
| [RateLimitEngine](https://github.com/peymanpro/RateLimitEngine) | A separate .NET rate-limiting library with in-memory and Redis-backed implementations |

The separation is intentional: each repository makes a different engineering boundary inspectable, while this project brings structured decisions, evidence provenance, quantitative reasoning, evaluation, and safety checks into one decision-support workflow.

## Design principles

**Decision-first** — model a bounded decision explicitly instead of silently turning every conversation into a permanent profile.

**Evidence before confidence** — insufficient evidence must remain visible.

**Deterministic where possible** — quantitative comparison, risk scoring, and sufficiency checks should be reproducible.

**AI as a component, not the system** — model calls remain behind explicit contracts.

**Human control** — consequential external actions stay outside the application's autonomous boundary.

**Auditable evolution** — research runs, decisions, and important changes should leave inspectable metadata.

**Conservative claims** — implemented behavior, measured outcomes, and roadmap intentions must remain distinct.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development expectations, testing commands, and pull-request guidance.

## License

MIT. See [LICENSE](LICENSE).
