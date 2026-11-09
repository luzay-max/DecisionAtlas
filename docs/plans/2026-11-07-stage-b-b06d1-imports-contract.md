# B06d-1 — Imports generated contract

**Status:** Implementation slice in progress; no merge authorization.

## Scope

Complete the existing Imports API contract without adding or duplicating routes:

- Import job queue/status/control responses use a shared DTO with the existing lifecycle states `queued`, `running`, `paused`, `succeeded`, and `failed`.
- Existing lookup and source-binding operations use one explicit target/source summary DTO, including nullable workspace, latest/active import and access-source status fields.
- Existing import capability and GitHub webhook responses receive explicit DTOs.
- The FastAPI routes attach response models with `response_model_exclude_unset=True` so fields omitted by an existing branch remain omitted while explicit `null` values stay `null`.
- Fastify BFF calls use generated OpenAPI operations for lookup, job creation/status/control, capabilities and source binding. The webhook remains on its raw-byte proxy path because GitHub HMAC verification depends on preserving the exact request bytes.
- GitHub tokens remain request-only. Request model repr hides token values; strict response DTOs reject unmodeled top-level credential fields.

## Compatibility invariants

- No new API, duplicate interface, schema migration, import worker behavior, or provider support.
- Preserve existing request validation, status/body passthrough, workspace/scope authorization and 502 transport envelope.
- Preserve import summary contents, job status/mode values, absent-vs-null response behavior and existing credential redaction.
- Pause/resume remains disabled by default. No enablement or state mutation is part of B06d-1.
- Do not log request bodies or tokens. Keep the webhook raw payload unchanged.

## Validation

- Engine tests cover job lifecycle DTOs, summaries, strict credential rejection, request repr redaction and existing import authorization/credential tests.
- BFF tests cover generated query/body/path calls, null values, token request-only behavior, error passthrough and default-off 503 behavior.
- TypeScript negative tests reject invalid paths/methods, missing query/body fields, arbitrary job states and response token fields.
- Regenerate Engine OpenAPI JSON and TypeScript declarations with the repository generator; run route-contract and DTO freshness checks.
- Run full Windows CI and PostgreSQL 17 CI on the exact final PR head.

## Follow-up

B06d-2 will separately cover Auth/Team DTOs, including login/session/scope compatibility and account/member management. B06e remains separate. #34 stays unmigrated, #36 stays disabled, and #47 remains integration-only.
