# Stage B / B06a — Engine OpenAPI route contract baseline

**最终状态（2026-11-07 更新）：B06a / PR #51 已于 2026-11-06 合并。本文记录的范围仍仅为路由／方法契约基础设施，不包含全量 DTO 或运行时行为变更。**

## Goal

Establish FastAPI Engine OpenAPI as the source of truth for HTTP path/method existence, and make the Fastify BFF's proxied Engine operations compile-time checked against that contract.

## Delivered in this slice

- Generate `apps/api/src/contracts/engine-routes.generated.ts` directly from `create_app().openapi()` using only the Engine's existing Python dependencies and the standard library.
- Record the 41 current Engine path/method operations as a generated TypeScript `EngineRoute` union.
- Maintain an explicit 39-operation Fastify BFF proxy inventory in `apps/api/src/contracts/engine-bff-routes.ts`, constrained with `satisfies readonly EngineRoute[]` so misspelled, removed, or method-mismatched Engine routes fail TypeScript checking.
- Add a focused test for manifest uniqueness/count and explicit local/deferred route exclusions.
- Add a Windows CI freshness check so the committed generated route contract cannot silently drift from the live FastAPI OpenAPI schema.

## Deliberate limits

- This is the **route/method foundation only**. It does not yet generate request/response DTOs, a typed fetch client, or complete parameter/body/response schemas.
- It does not normalize FastAPI `HTTPException.detail`, provider errors, BFF 502 responses, or define a shared error DTO. Those remain B06 follow-up work.
- Existing `apps/api/src/plugins/env.ts` Zod validation remains unchanged; production environment policy and cross-service validation remain separate follow-up work.
- The explicit BFF route inventory is a reviewed contract manifest. A later B06 slice should bind route declarations/fetch construction directly to generated operations and add request/response type checking.
- No Fastify BFF removal, API behavior change, database migration, production deployment, or credential operation.

## Acceptance

- [x] `uv run --project services/engine python services/engine/scripts/export_openapi_route_contract.py --check` passes on the exact PR head.
- [x] `pnpm test` and `pnpm typecheck` pass on the exact PR head.
- [x] The BFF manifest has no duplicate entries and every listed operation exists in the generated Engine OpenAPI contract.
- [x] Review confirms `/health` remains local to Fastify and the unexposed `/governance/rules/{draft_id}/lifecycle` operation is not accidentally added to the BFF inventory.
- [x] Independent review and explicit merge authorization.

## Unchanged gates

- #34 F06b migration remains unauthorized.
- #36 pause/resume remains default-off; listing its existing API operation does not enable it.
- #47 remains integration-only and must never be merged.
- Private-source operations and paid model calls remain separately gated.

## Final disposition — B06a / PR #51 merged

- Reviewed head: `d759cee33b3cc70264713ff5de587b5aa0610f47`.
- Merge commit: `9925c9e22c024f574ffbfc8e3ff7a99be5696e9f`.
- Post-merge Windows CI [#42192852069](https://github.com/luzay-max/DecisionAtlas/actions/runs/42192852069): **SUCCESS** (API 60, Web 104, Engine 581 passed / 9 skipped, Playwright 6; route freshness, typecheck, MCP, offline evidence and benchmark checks passed).
- Post-merge PostgreSQL 17 CI [#42192852563](https://github.com/luzay-max/DecisionAtlas/actions/runs/42192852563): **SUCCESS**.
- This is B06a only. B06b #52 separately completed the Why DTO slice; Decisions, Imports/Auth/Team, shared errors and environment validation remain subsequent work. No claim that full B06 is complete.
