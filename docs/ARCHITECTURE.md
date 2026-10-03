# Architecture

WealthBrain uses a modular monolith as its current architecture.

## Layers

```text
API
 ↓
Application Services
 ↓
Domain / Decision Engines
 ↓
Repository Interfaces
 ↓
SQLAlchemy / PostgreSQL

AI boundary
Application Service → AIProvider → Provider Adapter
```

The architecture keeps deterministic decision analysis independent from the AI provider.

## Current modules

- `api/conversations.py`: conversation HTTP boundary.
- `api/decisions.py`: decision workspace HTTP boundary.
- `modules/conversations/`: conversation persistence/application behavior.
- `modules/decisions/`: contracts, persistence, scoring, risk analysis, critique, and synthesis.
- `modules/ai/`: provider contracts, deterministic fake provider, and OpenAI-compatible adapter.
- `domain/`: durable domain primitives that should remain independent of infrastructure.
- `infrastructure/`: database and ORM mappings.

## Evolution rule

Do not introduce microservices only because a module exists. Split a component only when scale, ownership, isolation, or operational evidence justifies the boundary.
