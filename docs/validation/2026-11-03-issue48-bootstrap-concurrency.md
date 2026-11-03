# Issue #48 — local Bootstrap transaction race, isolated engineering acceptance

**2026-11-03 · Draft only.** Based on accepted `main@f2fae3949c2da9b1401ab14c1e0ff00c48592290` after B01 [post-main CI #41594072583](https://github.com/luzay-max/DecisionAtlas/actions/runs/41594072583) SUCCESS. Separate from B02/B03/B04 merge decisions and from #36 Worker concurrency.

## Trigger and scope

In [B02+B03 composition CI #41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746), the whole workflow and six Playwright cases succeeded, but ASGI logged `sqlite3.IntegrityError: UNIQUE constraint failed: actors.username` during concurrent **local/test** requests to `POST /auth/bootstrap`. The preexisting `ensure_bootstrap_identity` used `SELECT actor` followed by `INSERT actor` without serializing other sessions.

Only **local development and test** mode can use bootstrap; `AUTH_AUTO_BOOTSTRAP_LOCAL=false` or `APP_ENV=production` must still return 403 without opening the DB. This change does not enable auto-bootstrap in any nonlocal deployment.

## Proposed repair

- In `services/engine/app/api/auth.py`, acquire a **transaction-scoped** cross-session lock before the **first actor/scope read** in a fresh bootstrap session: `BEGIN IMMEDIATE` on SQLite, or `pg_advisory_xact_lock(1145132098, 480001)` on PostgreSQL. Lock holds through actor, scope and membership creation and issuance of the unique auth session, released on COMMIT/ROLLBACK. This is not a Python-only `threading.Lock`, so processes share the database boundary.
- Roll back on errors. On an unverified backend, fail rather than silently issue supposedly race-safe sessions.
- Never treat an existing *non-bootstrap* or disabled actor with the configured bootstrap username as local admin; likewise, a nonlocal owner-scope collision must not gain a new admin membership.
- No migration and no new schema constraint. The existing `owner_scope_memberships` table has no actor/scope composite uniqueness, so serializing the entire transaction is required; only making actor insertion idempotent would leave a second race.

## Acceptance and limits

- File-backed SQLite under real concurrent independent TestClient sessions: 2 and 8 requests against a fresh database, all 200; one actor/scope/admin membership, distinct valid durable session tokens and no 500.
- Reject preexisting normal actors, disabled bootstrap actors, and team-scope collisions without changing roles or creating sessions.
- Explicit production and feature-default-off 403 with no DB writes.
- Preserve Engine/Node/Playwright regression CI; review exact-head results and logs (particularly bootstrap tracebacks). Existing composed browser CI [#41595983746](https://github.com/luzay-max/DecisionAtlas/actions/runs/41595983746) was **green with a hidden log exception**, not a reproducible concurrency acceptance.
- A separate **Ubuntu/PostgreSQL 17 advisory-lock concurrency workflow** `.github/workflows/ci-bootstrap-concurrency-pg17.yml` now starts a disposable empty `pgvector/pgvector:pg17` database and runs eight simultaneous real `POST /auth/bootstrap` requests, asserting one actor/scope/membership, eight durable sessions and authorized token roundtrips. Its **exact-head CI must succeed**; Windows SQLite tests alone do not prove PG behavior. This is multi-connection PostgreSQL proof, not a true multi-host load/chaos test.
- Production reverse-proxy HTTPS, B03 Cookie/Origin hardening, #34 F06b migration, #36 worker recovery and P private data requirements remain independent and unchanged.

**Status: Draft, no merge authorization; CI result to be filled from exact Head.**
