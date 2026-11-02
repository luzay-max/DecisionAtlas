# Phase A — F01/F02 import controls and owner-scope session contract

**Date:** 2026-10-29
**Base:** `main@8aa461f5bc30f16e023c9c00f0d641794fd16f86` (merged PR #27, document-only)
**State:** Draft PR, not approved for merge. Independent of Draft PR #26.

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
