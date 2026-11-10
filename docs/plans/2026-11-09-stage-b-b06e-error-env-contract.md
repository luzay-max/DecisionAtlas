# B06e — API error contract and environment validation

**Status:** Implementation in progress in [Draft PR #58](https://github.com/luzay-max/DecisionAtlas/pull/58); production CORS fail-fast and credential/log redaction hardening are included. Latest exact-head CI is running; no merge or production authorization.

## Context

B06a–B06d established generated success DTOs and typed Engine operations for Why, Decisions, Imports, Auth and Team. Error handling is still inconsistent at the BFF boundary:

- FastAPI commonly returns `{"detail": ...}`, including a structured list for request validation.
- Fastify-owned validation and origin/auth failures use several existing `error` / `detail` shapes.
- Proxy transport failures currently return HTTP 502 with an internal error message in `detail`.
- The Web `readError` helper primarily understands `detail` and `error`, and does not consume a shared error code/message contract.
- Fastify environment validation currently provides permissive development defaults and does not fully validate URL, port, cookie-name and CORS-origin constraints. In particular, production must not silently inherit local bootstrap behavior.

B06e must make these contracts explicit without silently changing HTTP status semantics or exposing secrets.

## Proposed scope

### 1. A stable BFF error envelope

Introduce one BFF-owned error DTO, separate from Engine success DTOs:

```ts
type ApiErrorCode =
  | "unauthenticated"
  | "forbidden"
  | "invalid_request"
  | "not_found"
  | "conflict"
  | "request_rejected"
  | "upstream_unavailable"
  | "internal_error";

type ApiErrorResponse = {
  code: ApiErrorCode;
  message: string;
  detail?: unknown;
  error?: string;
  issues?: unknown;
};
```

The implementation must:

- Preserve the existing HTTP status code for each response; the new code is descriptive and must not become a status remapping mechanism.
- Preserve legacy `detail`, `error` and `issues` fields for 4xx responses where present so existing consumers can migrate incrementally. For 5xx, do not expose upstream exception details; return a generic public message and retain diagnostics only in server logs.
- Put scalar upstream error bodies in `detail` rather than dropping or double-parsing them.
- Map 401 → `unauthenticated`, 403 → `forbidden`, 400/422 → `invalid_request`, 404 → `not_found`, 409 → `conflict`, 502/504 → `upstream_unavailable`, 503 → `service_unavailable`; other 4xx → `request_rejected`, other 5xx → `internal_error`.
- Give BFF-owned validation/auth/origin failures the same code/message fields while retaining their current legacy fields.
- Keep success payloads, response statuses, cookie behavior and all route authorization unchanged.
- Return a generic public message for network/transport failures; keep only safe error type/code metadata in server logs; never log raw exception messages/stacks, request bodies, passwords, cookies, session tokens, GitHub tokens, API keys or raw environment values.
- Update Web error parsing to prefer the new `message`, then fall back to legacy `detail` / `error`.

The error DTO belongs to the BFF contract, not the Engine success OpenAPI models. Do not add a second manually maintained copy in Web; export/reuse one shared type from the contract package or a clearly scoped API-contract module.

### 2. Fastify environment validation

Strengthen the BFF `getEnv` schema and startup behavior:

- `PORT`: integer in 1–65535.
- `ENGINE_BASE_URL`: absolute HTTP(S) URL with no embedded credentials, query, fragment or surrounding whitespace.
- `AUTH_COOKIE_NAME`: valid cookie-token name; reject separators, whitespace and control characters.
- `CORS_ALLOWED_ORIGINS`: comma-separated exact HTTP(S) origins only (no wildcard, path, query, fragment or credentials); in production at least one explicit origin is required. For same-origin reverse-proxy deployments, list the public Web origin because state-changing browser requests include an Origin header. Empty is allowed only in development/test.
- Preserve current development/test defaults and boolean parsing.
- In `APP_ENV=production`, require an explicitly configured `ENGINE_BASE_URL`; do not silently use the local development default.
- In `APP_ENV=production`, reject `AUTO_BOOTSTRAP_AUTH=true`; anonymous bootstrap is a local-only convenience and must fail closed in production.
- Validation errors must identify the variable and constraint without echoing the rejected value.
- Validate once before listening; tests may still pass explicit environment objects to `getEnv`.

This slice is limited to the Fastify BFF environment contract. Engine database/provider/bootstrap production policy requires a separate explicit review and is not silently changed here.

## Compatibility and security invariants

- Preserve all existing HTTP status codes and authorization decisions (401/403/400/404/409/422/502/503).
- Preserve upstream success bodies byte/JSON semantics; only error response envelopes gain the additive contract.
- Preserve existing Engine error details and validation issue structures as legacy fields; do not invent a successful response on parse failure.
- No credential echo, request-body logging, token logging or raw exception detail in client-facing 5xx messages.
- No new routes, database migrations, backfills, session format changes, cookie policy changes or role changes.
- #34 remains unmigrated; #36 remains default-disabled; #47 remains integration-only and must never be merged.
- No production deployment, credential rotation, private-source operation, paid model call or worker enablement.

## Required tests

### Error contract
- Unit tests for status-to-code mapping and legacy-field preservation.
- BFF route tests for 400/401/403/404/409/422 and upstream 500/502/503/504.
- FastAPI `detail` string, object and validation-array bodies; JSON scalar and plain-text error bodies.
- Transport timeout/network rejection returns 502 with generic public message and no internal error detail. 500/502/504 responses must not echo exception messages or secrets; logs retain only safe error type/code metadata. The deliberate 503 feature-disabled response (especially #36 pause/resume) must retain its safe explanatory detail and remain HTTP 503.
- Verify status codes do not change and existing UI callers can read both new and legacy forms.
- Verify passwords, session cookies/tokens, GitHub tokens, API keys and request bodies never appear in response or logs; cover snake_case, kebab-case and camelCase credential-key variants and ensure raw exception messages/stacks are not logged.

### Environment contract
- Table-driven tests for valid/invalid port, Engine URL, cookie name and origin allowlist.
- Preserve development/test defaults and accepted boolean spellings.
- Production requires explicit Engine URL and rejects auto-bootstrap.
- Error messages name the invalid setting but never echo its value.
- Startup fails before listening when configuration is invalid.

### CI and review
- Full Windows CI on the exact PR head (covers API/Web tests, typecheck, Engine suite, offline regression, benchmark fixtures and Playwright).
- PostgreSQL 17 merged-schema CI is required if the slice changes Engine code/schema; Bootstrap concurrency PG17 is required if it changes Engine auth concurrency code/tests. B06e is BFF/Web-only and touches neither path, so these specialized workflows are not applicable to this slice.
- OpenAPI/contract generation freshness checks remain green; no generated success DTO drift.
- Independent technical review must inspect status/body compatibility and credential redaction separately from implementation.
- Explicit maintainer merge approval remains a separate gate.

## Suggested implementation sequence

1. Add shared BFF error DTO and pure normalization helpers with exhaustive unit tests.
2. Apply the helper consistently to BFF-owned errors and Engine-proxy errors without changing status codes.
3. Update Web error parsing to consume `message` while retaining legacy fallback.
4. Tighten Fastify environment parsing and startup fail-fast behavior.
5. Add exact status, payload, redaction and environment regression suites.
6. Run exact-head CI, independent review and wait for explicit merge approval.

## Relationship to completed B06 slices

- B06a: Engine OpenAPI route/method baseline.
- B06b: typed Why contract.
- B06c: Decisions list/detail/review contract.
- B06d-1: Imports generated contract, merged in PR #55.
- B06d-2: Auth/Team generated contract, merged in PR #56 at `6b107f77c016e8f6e258b6c527206c1a212af7bf`; post-merge Windows full CI, PostgreSQL 17 merged-schema CI and Bootstrap concurrency PG17 all passed on that exact main commit.

B06e is the next proposed Stage B contract slice. It does not start B07 or C01 and does not relax any existing boundary.
