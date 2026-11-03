# Stage B / B03 — same-origin Web API and robust HttpOnly session boundary

**2026-11-03, Draft implementation, no merge authority.** Branch from accepted Stage A `main@2641989b443ca6633019fa7b713521be0ce5686d`. B01 [Draft #43](https://github.com/luzay-max/DecisionAtlas/pull/43) and B02 [Draft #44](https://github.com/luzay-max/DecisionAtlas/pull/44) are **separate, not merged or stacked**. No #34 schema migration, #36 pause enablement, paid AI or private source operations.

## Existing behavior and security gap

- `apps/web/lib/api.ts` used `API_BASE_URL ?? http://127.0.0.1:3001` directly in the browser. On a remote client, that address refers to **the user's own computer**, not DecisionAtlas' API. This required cross-origin credential handling and often mismatched cookie scope.
- The Web session provider wrote the BFF's session token to JavaScript-readable `localStorage`, despite the BFF already issuing `HttpOnly; SameSite=Lax` cookies. A client-side script did not need to retain another copy of that credential.
- `apps/api/src/auth.ts` did an unchecked `decodeURIComponent` on arbitrary Cookie header values; malformed percent encoding caused a thrown `URIError`. Duplicate cookie names could overwrite the selected session.

## Changes

1. Next.js server-only `API_BASE_URL` config now rewrites browser requests under **same-origin** `/backend/:path*` to the configured fixed BFF upstream; the Web client no longer exposes a machine-local API port or uses browser `credentials: include` across origins.
2. **Subsequent browser authentication** uses the BFF's `HttpOnly` session cookie, not a JavaScript `localStorage` token/header. Previously stored `decisionatlas-session-token` values are erased, not updated. Session and scope recovery continue via existing API routes. **Compatibility limit:** login/session JSON still contains `session_token`; removing that returned field requires a separate API-contract migration, so this PR does not claim JS can never observe a token.
3. SSR continues to use the server-only API target but forwards **only** the configured `AUTH_COOKIE_NAME`, instead of every browser cookie. Nothing is logged or persisted from these values.
4. Cookie parser handles malformed encoding, duplicate names, control bytes and excessively long headers by rejecting cookie values; it uses a null-prototype map and does not take arbitrary `x-decisionatlas-session-token` headers from the browser as auth. A valid encoded token is passed to Engine as before.
5. Keep Fastify's origin gate: in production deployments, `CORS_ALLOWED_ORIGINS` must explicitly include the **public Web origin** because the proxied state-changing request may carry that Origin. Do **not** wildcard this allowlist or suppress origin validation. Existing Secure/SameSite cookie attributes remain unchanged.

## Acceptance tests and deployment caveats

- API tests: malformed percent/control bytes and duplicate cookie names give 401 (not 500) with **no Engine fetch**, valid encoded token forwards correctly, forged direct session header is ignored.
- Web tests: `/backend/auth/login` and `/backend/query/why` use same-origin credentials; no localStorage session token or raw session header, even if old localStorage data exists. Existing browser auth flow tests updated to require **no JS-readable token storage**.
- CI: latest-head Node/typecheck + Engine + browser smoke, with explicit security test review. End-to-end live remote-host proxy/session validation with real TLS and proxy headers is a separate deployment gate; do **not** claim a real production run from mocked CI.
- Deploy with `API_BASE_URL` pointing to a trusted *server-reachable* BFF origin, not browser's localhost; keep reverse-proxy HTTPS and origin allowlist aligned. No runtime feature flag or migration.

**Status: Draft/unmerged, explicit maintainer approval required.** B01/B02 approval/merge requires independent checks. If main changes first, update this branch and rerun exact-head CI.
