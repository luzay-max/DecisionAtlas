# B06c — Decisions list/detail/review generated contract

**Status:** Draft implementation slice; based on `main@64030926fe7fb7a6dbb76bab980a10571beb199e`. No merge authorization.

## Scope

Complete the next existing vertical slice after B06b by modeling the current Decisions API without adding endpoints:

- `GET /decisions` list response, including evidence summary, source-reference preview, current quote integrity and candidate quality.
- `GET /decisions/{decision_id}` detail response, including full source references and review history.
- `POST /decisions/{decision_id}/review` request and response, including the audit event and review history.

Engine response models are strict and attached to the existing FastAPI routes. The existing serializer, workspace role checks, review-state validation, and status codes remain the source behavior.

The shared `@decisionatlas/engine-contract` package exports generated query, request and response types. The Fastify BFF consumes the generated operations through `openapi-fetch`; Web API wire types are aliases to those generated types. A separate UI view projection permits sparse in-memory demo fixtures without weakening the HTTP response contract.

## Compatibility invariants

- Keep source-ref IDs, quote text, span offsets, nullable URLs, relevance scores and `current_quote_match` unchanged.
- Keep `review_state`, candidate-quality labels, current-quote-integrity states, audit event fields and review-history ordering unchanged.
- Preserve explicit `null` values and empty arrays; do not synthesize missing provenance.
- Keep list/detail/review response shapes distinct: the review mutation response does not gain list/detail-only provenance fields.
- Do not change reviewer/viewer role gates, owner-scope isolation, 400 invalid review-state behavior, 401/403/404/422 responses, or BFF 502 transport handling.
- No new route, schema migration, backfill, worker behavior, private-source action or paid model call.

## Validation

- Engine API tests: full response model validation, nullable/empty cases, review-state mutation, existing invalid-state and not-found status behavior.
- BFF tests: typed path/query/body, response passthrough, null/empty collections, and existing error/transport envelopes.
- TypeScript negative tests: invalid paths/methods, missing query/path/body fields, wrong field types and nullable values.
- Regenerate and freshness-check Engine OpenAPI JSON and TypeScript declarations.
- Run full Windows CI and PostgreSQL 17 CI on the exact final PR head.

## Boundaries

#34 remains unmigrated; #36 remains disabled; #47 remains integration-only and must not be merged. B06d (Imports/Auth/Team) and B06e (error DTO/environment validation) remain separate follow-ups.
