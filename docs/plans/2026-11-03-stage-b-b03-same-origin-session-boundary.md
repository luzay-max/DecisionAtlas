# Stage B / B03 — same-origin Web API and robust HttpOnly session boundary

**2026-11-05 · Draft implementation, no merge approval.** B01 #43 and B02 #44 are independently merged into `main@0df1b2be3b5fb3dbf7a09c558f18f7ab666191f7`; post-B02 main CI [#41960827789](https://github.com/luzay-max/DecisionAtlas/actions/runs/41960827789) is SUCCESS. B03 #45 is updated onto this main. The shared `apps/web/lib/api.ts` uses the composed version previously verified on integration-only #47, retaining B02's typed retrieval-mode contract while applying B03's same-origin cookie transport. B02+B03 composed regression tests from #47 are now carried in #45 itself. **#47 remains integration-only and must not be merged.**

No #34 schema migration, #36 pause/resume enablement, paid AI or private-source operations P are included or authorized.

## Existing behavior and security gap

- `apps/web/lib/api.ts` previously used `API_BASE_URL ?? http://127.0.0.1:3001` directly in the browser. On a remote client, that address refers to the visitor's own computer, not the deployed API.
- The Web session provider wrote the BFF session token to JavaScript-readable `localStorage`, despite the BFF already issuing an `HttpOnly; SameSite=Lax` cookie.
- `apps/api/src/auth.ts` previously decoded arbitrary Cookie header values without guarding malformed percent encoding; duplicate names could overwrite the selected session.

## Changes retained in this candidate

1. Next.js server-only `API_BASE_URL` rewrites browser requests under **same-origin** `/backend/:path*` to a fixed configured BFF upstream. Browser code never connects to a machine-local port or uses cross-origin `credentials: include`.
2. Subsequent browser authentication uses the BFF's **HttpOnly** session cookie, not a JavaScript-readable `localStorage` token/header. Old `decisionatlas-session-token` values are erased. Session/scope recovery stays on existing routes.
3. SSR forwards only the configured `AUTH_COOKIE_NAME` to the internal BFF, not every browser cookie.
4. Cookie parsing rejects malformed encoding, duplicate names, control bytes and oversized headers; it uses a null-prototype map. A forged `x-decisionatlas-session-token` browser header is not trusted.
5. Keep the production Origin gate. `CORS_ALLOWED_ORIGINS` must explicitly include the public Web origin; do not wildcard the allowlist or suppress Origin validation. Existing Secure/SameSite cookie attributes remain unchanged.
6. The shared typed Web API preserves B02's `RetrievalMode` (`lexical_only`, `lexical_fallback`, `hybrid`) and its root/`answer_context` contract while using B03 same-origin cookie transport.

**Compatibility limit:** login/session JSON still contains `session_token`; removing that returned field requires a separate API-contract migration. This PR does not claim JavaScript can never observe a token. Subsequent browser requests must not persist or forward that token from localStorage.

## Acceptance tests

- API cookie parser tests: malformed encoding/control bytes, duplicate names, oversized headers, valid encoded tokens and forged direct session headers.
- Web unit tests: same-origin `/backend`, `credentials: same-origin`, no localStorage token and no client session header.
- **B02+B03 composition tests copied from #47:** BFF preserves Chinese Why payload and `retrieval_mode` while forwarding only the validated cookie; hostile Origin is blocked; duplicate cookie fails closed. Web typed client preserves `lexical_only`, `lexical_fallback`, and `hybrid` through same-origin transport.
- **Real browser composition smoke:** Web → Next rewrite → Fastify BFF → FastAPI Engine; synthetic Chinese/English accepted decision and candidate-only negative fixture; HttpOnly/SameSite=Lax cookie, hostile Origin 403, no browser request to localhost:3001 and no JS-readable localStorage token.
- The synthetic fixture is created only by `scripts/ci/seed_b02_b03_composition.py` in the disposable CI database. No real repository capture, private content or paid provider.

The previous integration-only #47 exact-head CI [#41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746) passed. The copied tests must now pass again on the **updated exact #45 head**, alongside the complete Node/typecheck, Engine, MCP, offline evidence, benchmark and Playwright main workflow.

## Deployment caveats and independent gates

- Live remote-host HTTPS, reverse-proxy headers, Secure-cookie behavior and production Origin allowlist are a separate deployment acceptance; mocked/unit CI is not production proof.
- Set `API_BASE_URL` to a trusted server-reachable BFF origin, never the visitor's localhost.
- B03 remains an independent Draft and needs its own maintainer approval after exact-head CI and review. #44 approval does not authorize #45.
- #47 remains a test-only integration record; do not merge it.
- #34 migration, #36 pause/resume and private-data P remain unchanged and outside this PR.

**Status: Draft/unmerged; updated main baseline and composed regression tests require exact-head CI.**
