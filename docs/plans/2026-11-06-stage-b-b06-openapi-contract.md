# Stage B / B06a — Engine OpenAPI route contract baseline

**2026-11-06 · Draft implementation slice · No merge or runtime behavior change.**

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

- [ ] `uv run --project services/engine python services/engine/scripts/export_openapi_route_contract.py --check` passes on the exact PR head.
- [ ] `pnpm test` and `pnpm typecheck` pass on the exact PR head.
- [ ] The BFF manifest has no duplicate entries and every listed operation exists in the generated Engine OpenAPI contract.
- [ ] Review confirms `/health` remains local to Fastify and the unexposed `/governance/rules/{draft_id}/lifecycle` operation is not accidentally added to the BFF inventory.
- [ ] Independent review and explicit merge authorization.

## Unchanged gates

- #34 F06b migration remains unauthorized.
- #36 pause/resume remains default-off; listing its existing API operation does not enable it.
- #47 remains integration-only and must never be merged.
- Private-source operations and paid model calls remain separately gated.

