# B06d-2 — Auth / Team generated contract

**Status:** MERGED and accepted on 2026-11-09; independent technical review and post-merge main validation passed.

## Scope

Complete the existing Auth and Team API contracts without adding or duplicating routes:

- Auth bootstrap, login, logout, session recovery and owner-scope switch responses use explicit strict DTOs.
- Preserve the existing response distinction: bootstrap includes actor status but not available scopes; login includes actor status and available scopes; session and scope-switch include available scopes but preserve the current actor shape.
- Team account list/create/disable/password-reset/role-update and workspace-member list/assign/remove responses use explicit strict DTOs.
- Account and member role/status values are finite, nullable member-actor role is represented explicitly, and Team response DTOs reject password/session-token fields.
- Fastify BFF calls use generated OpenAPI operations and request types for every existing Auth/Team operation.
- Web API aliases its Auth/Team request and response types to `@decisionatlas/engine-contract`; no duplicate handwritten wire DTOs remain.

## Compatibility invariants

- No new route, duplicate interface, database migration, role change, session format change, cookie policy change, or authorization change.
- Preserve the session token field in existing Auth JSON responses for compatibility; the BFF continues to set the HttpOnly cookie and never stores new tokens in localStorage.
- Preserve cookie-only session forwarding. Never accept a browser-supplied `x-decisionatlas-session-token` header or forward unrelated cookies.
- Preserve login/bootstrap/session/scope payload shapes, including actor bootstrap/status differences and available-scope ordering.
- Preserve Team account/member response envelopes, nullable display name/member actor role, role/status values, and all existing 400/401/403/404/409/422 semantics.
- Preserve upstream status/body passthrough and the existing 502 transport-failure envelope.
- Team responses must not expose passwords or session credentials. No request body or credential logging.

## Validation

- Engine response models are attached to all 13 existing Auth/Team operations; OpenAPI JSON and TypeScript declarations are regenerated from FastAPI and freshness-checked.
- Engine tests assert exact response references, strict response schemas, auth variant distinctions, nullable member actor role and credential rejection.
- BFF tests cover session-cookie forwarding, generated body/path calls, logout clearing, errors and status passthrough.
- TypeScript negative tests reject invalid routes/methods, missing request fields, invalid path params, wrong field types and response credential fields.
- Web type aliases use generated DTOs and existing UI/session tests pass with complete wire fixtures.
- Full Windows CI and PostgreSQL 17 CI must pass on the exact PR head before independent review.

## Disposition and final verification

- PR [#56](https://github.com/luzay-max/DecisionAtlas/pull/56) was merged after explicit maintainer approval.
- Reviewed PR head: `7a14979a30868c8872205ba8a81f61f493de7137`.
- Merge commit / verified `main` HEAD: `6b107f77c016e8f6e258b6c527206c1a212af7bf`.
- Independent technical review: PASS; no blocking findings on the reviewed head.
- Exact-head pre-merge validation passed: Windows full CI #42585866128, PostgreSQL 17 #42585866199, Bootstrap concurrency PG17 #42585866189.
- Post-merge validation on the merge commit passed:
  - [Main full CI #42592357235](https://github.com/luzay-max/DecisionAtlas/actions/runs/42592357235) — SUCCESS.
  - [PostgreSQL 17 merged-schema #42592357358](https://github.com/luzay-max/DecisionAtlas/actions/runs/42592357358) — SUCCESS.
  - [Bootstrap concurrency PG17 #42592357079](https://github.com/luzay-max/DecisionAtlas/actions/runs/42592357079) — SUCCESS.
- No database migration, backfill, production rollout, credential reset, or worker enablement was performed.

## Boundaries

#34 remains unmigrated; #36 remains default-disabled; #47 remains integration-only. B06e stays separate. No B07 or later-stage work starts as part of this slice.
