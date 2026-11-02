# Phase A — F01/F02 import controls and owner-scope session contract

**Date:** 2026-10-29
**Base:** `main@28b58eb1388c25a0a1ab3f1cca3c1848da4c2a0c` (A01/A02 merged)
**State:** Existing Draft PR #28, rebased onto current main; no merge authorization. A03 UI controls remain disabled unless the Engine explicitly reports the capability enabled.

## Problems and bounded fixes
- **F01:** Browser posts `/imports/:jobId/pause` and `/resume` to Fastify, but Fastify lacked these routes. Add **two explicit POST routes**, validate the job ID, pass only the existing cookie-derived session context and proxy Engine status/payload unchanged. No new privilege is granted; Engine still authorizes actions per workspace and requires admin.
- On the dashboard, remove empty catch blocks; only change rendered job state after a successful, matching Engine response. Show errors, avoid concurrent duplicate clicks, preserve old status on failure.
- **F02:** Engine `POST /auth/scope` returns only three fields while browser `ProductSessionProvider` replaces its entire session with that response. Return actor, current role, membership list, and token from the verified actor and target membership. Failed/missing membership cannot mutate the stored session.

## Automated tests
- [ ] BFF pause/resume 200 and 401/403/404/400 status forwarding, caller credential forwarding and invalid action/job ID rejection.
- [ ] Engine scope switch validates full response, session read after switch, denied/missing memberships, and role revocation on protected import action.
- [ ] Fastify scope proxy returns complete schema without dropping actor/membership fields.
- [ ] UI/TypeScript checks: no optimistic paused/running status after an error; user-visible error and duplicate-action lockout.
- [ ] Full Windows GitHub Actions on final branch head passes.

## Explicit limits
- GitHub Actions mock and ephemeral SQLite tests are **not** a local operator or customer-host trial. Browser pause responsiveness, long-running task atomicity, authorization/CSRF in real deployment, and cross-scope in-flight cache races still need integration acceptance.
- Do not merge this PR or #26 without later explicit approval. Do not introduce real tokens, paid model API calls, private-repository imports, database migrations, or unrelated features.


## A02 default-off capability integration (2026-11-02)

A02 merged the Engine setting `IMPORT_PAUSE_RESUME_ENABLED=false` by default and returns HTTP 503 from pause/resume while worker lifecycle safety remains unverified. A03 must not present those controls as usable.

- Engine exposes authenticated read-only `GET /imports/capabilities` returning `pause_resume.enabled` and `reason_code`. The Engine is the single source of truth; the BFF proxies the response with the cookie-derived session token and unchanged upstream status/body.
- Web loads this capability before rendering controls. It shows Pause/Resume only when `enabled === true`; when disabled, it explains the worker-lifecycle gate; if capability lookup fails, it fails closed and keeps controls hidden.
- This is a presentation/API contract only. It does **not** fix SQLite active-writer contention, durable worker leases, restart recovery, extraction-time pause, or cancellation. Issue #36 remains open; do not enable the environment flag in production.
- Scope-switch test opts into the experimental flag explicitly because it verifies authorization isolation, not production readiness. A separate Engine test verifies the default-off capability response and unauthenticated 401.
- Existing BFF tests cover status pass-through (including 409) and 502 network failure. Engine currently returns 400 for invalid state transitions; a 409 response is only a forwarding compatibility case, not a claimed Engine behavior.
