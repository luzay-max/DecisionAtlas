# DecisionAtlas v0.3 Real Stack Validation Report

Date: 2026-04-28 09:52 +08:00  
Change: `validate-v0-3-real-stack-flow`  
Baseline commit before validation: `6618a28` (`Prepare v0.3 release candidate baseline`)  
Branch: `main`  
Validation mode: local deterministic checks first; provider-dependent checks are recorded as operator-guided limitations unless credentials/configuration are available.

## Summary

Status: complete with environment-limited real-stack coverage

This report validates the v0.3 RC product baseline across the local demo lane, real local stack, public repository import path, platform access surfaces, hosted operator checks, and canonical release gate. It intentionally does not expand product scope; findings are classified as `pass`, `blocking`, `non-blocking`, or `known limitation`.

No product-code blocking issue was found in deterministic checks. The only uncompleted real-stack/live-import coverage is environment-limited: Docker Desktop was not running, so the Postgres/Redis real stack could not start in this session.

Conclusion: v0.3 is ready to proceed to the next planned productization phase for code paths covered by deterministic validation. Before claiming hosted preview or full real-stack validation readiness, rerun the real Postgres/Redis stack and public import matrix with Docker Desktop running.

## Supported Command Inventory

| Area | Command / action | Notes |
| --- | --- | --- |
| Real local stack start | `pnpm run dev:real` | Calls `scripts/dev/start-real-stack.ps1`; starts Docker Postgres/Redis, runs migrations/seed, starts engine/API/web. |
| Real local stack stop | `pnpm run dev:real:stop` | Calls `scripts/dev/stop-real-stack.ps1`; stops managed ports and Docker Postgres/Redis. |
| Real stack batch start | `scripts/dev/start-real-stack.bat` | Windows convenience wrapper for the same real stack path. |
| Real stack batch stop | `scripts/dev/stop-real-stack.bat` | Windows convenience wrapper for real stack shutdown. |
| Hosted/demo health | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1` | Checks web, API health, engine health, and optional dependency reachability. |
| Hosted/demo smoke | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1` | Runs health check and Playwright demo smoke against an already running web URL. |
| Seeded demo reset | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1 -UseLocalDemoDatabase` | Resets the seeded `demo-workspace` lane without deleting imported workspaces. |
| Seeded demo reseed | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reseed-demo.ps1 -UseLocalDemoDatabase` | Rebuilds the seeded demo lane after migration/data drift. |
| Canonical release gate | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` | Mandatory local release validation gate. |
| Auth/session validation | component/API tests and `/auth/session` in running stack | Session recovery uses bootstrap in local stack. |
| Scope switching validation | component/API tests and account scope UI | Owner scope switching is product-visible when multiple scopes are available. |
| Role gates | component/API tests and admin/reviewer panels | Admin-only setup panels and reviewer/admin review gates are enforced by product components. |
| GitHub App binding | component/API tests and admin panel | Full OAuth/Marketplace installation remains out of scope. |
| Private repo binding | component/API tests and admin panel | Requires operator-provided token for real private repositories; token must not be echoed. |
| Public repo import | running stack import UI/API | Provider/network dependent when hitting live GitHub. |

## Validation Matrix

| Lane | Command / action | Observed result | Status | Known limitation | Follow-up |
| --- | --- | --- | --- | --- | --- |
| Baseline | `git rev-parse --short HEAD`; `git status -sb` | `6618a28`; `main...origin/main`; only this active OpenSpec change untracked before validation. | pass | Working tree includes this validation change during execution. | None. |
| Command inventory | inspected `package.json`, `scripts/dev`, `scripts/demo`, `scripts/ci`, and current tests | Current supported commands listed above. | pass | None. | None. |
| Seeded demo lane | `scripts/dev/start-demo-stack.ps1`; `scripts/demo/health-check.ps1 -SkipDependencyChecks`; `scripts/demo/smoke-check.ps1`; `scripts/demo/reset-demo.ps1 -UseLocalDemoDatabase`; `scripts/demo/reseed-demo.ps1 -UseLocalDemoDatabase` | Demo stack started; web/API/engine health passed; Playwright demo smoke `1 passed`; reset and reseed completed for `demo-workspace`. | pass | Demo stack uses local SQLite smoke/demo mode, not the recommended real-import database path. | None. |
| Real local stack | `pnpm run dev:real` | Startup stopped existing stack, then failed connecting to Docker Desktop Linux engine; Postgres port 5432 was not listening. | known limitation | Docker Desktop daemon was not running in this environment. Real Postgres/Redis stack was not validated in this session. | Rerun `pnpm run dev:real` after Docker Desktop is running before hosted preview readiness. |
| Public repository import | `GET /imports/lookup?repo=psf/requests`; `POST /imports/github` on the running demo stack | Lookup succeeded with public access label. Import reached GitHub artifact collection but failed during sqlite-backed extraction progress update with `sqlite3.OperationalError: database is locked`. | non-blocking | Live public imports should be validated on the real Postgres/Redis stack, not the SQLite demo stack. Real stack could not run because Docker was unavailable. | Rerun public import on real stack after Docker is available; keep as input to `validate-v0-3-real-stack-flow` archive notes if not rerun. |
| Canonical release gate | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` | Passed. Workspace tests/typechecks passed; API `25 passed`; web `55 passed`; engine pytest `162 passed`; offline benchmark fixtures loaded; Playwright smoke `1 passed`. | pass | Release gate uses deterministic smoke/fixture validation, not live provider credentials. | None. |
| Session and scope | API tests `auth-route.test.ts`; web tests `auth-session-flow.test.tsx`; running stack `/auth/session` | API tests `4 passed`; web session tests `5 passed`; running stack returned bootstrap admin session for `local-default`. | pass | Running local stack only exposes the bootstrap scope unless seeded/test data provides multiple scopes. | None. |
| Role gates | Web tests including admin/reviewer gates; API imports/auth route tests | Admin-only GitHub App/private access panels hide setup actions for reviewer role; review gates remain reviewer/admin bounded; targeted web tests `23 passed`; targeted API tests `12 passed`. | pass | Role validation is component/API-level in this session, not a multi-user hosted run. | None. |
| GitHub App binding | `github-app-installation-panel.test.tsx`; `imports-route.test.ts` | Binding panel tests `3 passed`; API import route tests include installation binding proxy; access-source label rendering verified in dashboard/live-analysis tests. | pass | Full OAuth/Marketplace installation and production webhook configuration remain out of scope. | Next roadmap: `productize-github-app-sync-operations`. |
| Private repo binding | `private-repo-access-panel.test.tsx`; `imports-route.test.ts` | Private access panel tests `3 passed`; API private binding proxy covered; token non-echo behavior verified; access-source result label verified. | pass | Real private repository import requires operator-provided credentials and was not run. | Next roadmap: `harden-private-repo-access-operations`. |
| Hosted health/smoke | `scripts/demo/health-check.ps1 -SkipDependencyChecks`; `scripts/demo/smoke-check.ps1` | Health passed for web/API/engine; hosted guided-demo smoke passed against local running web URL. | pass | This was local hosted-operator rehearsal, not an external hosted preview. | Next roadmap: `prepare-v0-3-hosted-preview`. |
| OpenSpec validation | `openspec validate validate-v0-3-real-stack-flow --type change --strict --json`; `openspec validate release-baseline-validation --type spec --strict --json` | Change validation passed; existing modified main spec validation passed. Direct validation of new `v0-3-real-stack-validation` main spec is expected to be unavailable until archive creates it. | pass | New capability is still a delta spec before archive. | Archive after review to create the main spec. |

## Deferred Follow-Up Areas

- GitHub App sync operations productization: add visible sync origin/history and webhook operator verification.
- Private repo access hardening: improve real credential failure taxonomy and status display after running credential-backed validation.
- Real repo decision value quality: revalidate accepted baseline quality after real-stack import can run on Postgres.
- Hosted preview readiness: rerun health/smoke/reset/reseed on the externally hosted environment.
- Environment prerequisite: Docker Desktop must be running before claiming real Postgres/Redis stack validation.

## Blocking Assessment

- Product-code blockers found: none.
- Environment blockers found: Docker Desktop daemon unavailable for real Postgres/Redis stack validation.
- Non-blocking validation finding: live public import on the SQLite demo stack can hit `database is locked`; validate live imports on the real Postgres/Redis stack instead.

## Cleanup

- Real stack cleanup command: `pnpm run dev:real:stop`.
- Cleanup status: demo stack stopped with `scripts/dev/stop-demo-stack.ps1`; no listeners remained on ports 3000, 3001, or 8000 after validation.
