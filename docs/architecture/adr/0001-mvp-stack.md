# ADR-0001: Use A Next.js + Fastify + Python Engine MVP Stack

## Status
Accepted

## Context

DecisionAtlas needs a stack that one developer can ship in an MVP window without losing separation between UI, API boundaries, and AI-heavy backend logic.

The stack must:

- support a modern browser UI
- keep TypeScript on frontend and integration edges
- keep Python where retrieval and extraction logic will evolve fastest
- run locally with low setup cost

## Decision

Use:

- `Next.js + TypeScript` for the web app
- `Fastify + TypeScript` for the API edge
- `FastAPI + Python` for the engine service
- `PostgreSQL + pgvector` for storage
- `Redis` for background job coordination
- `Docker Compose` for local development

## Consequences

### Positive

- keeps the product surface and AI-heavy logic cleanly separated
- matches the strengths of TypeScript and Python
- is straightforward to run on one machine

### Negative

- introduces multi-runtime complexity from day one
- requires coordination across Node and Python tooling

### Neutral

- the engine can start as a single service and split later if needed

## Alternatives Considered

- Monolithic Next.js app with all logic inside route handlers
- Full microservice split for ingest, retrieval, extraction, and drift from day one

## References

- [Implementation Plan](../../plans/2026-03-18-decisionatlas-implementation-plan.md)
