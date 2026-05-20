# 2026-05-20 Update Log

## Summary

- Established the team self-hosted product direction: small-team private deployment, administrator-created accounts, token-paste Git access first, no hosted SaaS billing or Marketplace/OAuth dependency.
- Implemented and archived OpenSpec change `team-account-workspace-permissions`.
- Added local team account lifecycle, workspace membership permissions, and an admin-only team management surface.
- Updated self-hosted commercial documentation and OpenSpec main specs to include the new team-account and workspace-permission baseline.

## Completed Changes

### Team self-hosted product plan

- Added `docs/plans/2026-05-20-decisionatlas-team-self-hosted-development-plan.md`.
- Reframed DecisionAtlas as a self-hosted code decision governance collaboration product, not a Git hosting replacement.
- Prioritized the next development sequence: team accounts/workspace permissions, multi Git source import, collaborative audit trail, offline self-hosted release package, team reporting, and support/license boundary.

### Team account and workspace permissions

- Archived OpenSpec change: `2026-05-20-team-account-workspace-permissions`.
- Added account status fields so disabled users cannot log in or recover existing sessions.
- Added workspace membership storage and effective workspace role resolution.
- Added admin-only engine endpoints for account creation, disabling, password reset, role assignment, and workspace member management.
- Added API gateway `/team/*` forwarding with session-cookie propagation and no typed owner-scope override for sensitive actions.
- Added Web `/team` admin surface for managing accounts and workspace members.
- Tightened product role gates so unauthorized states show permission copy instead of missing-data copy.

### Specs and documentation

- Synced delta specs into main OpenSpec specs:
  - `login-roles-and-workspace-scoping`
  - `team-account-management`
  - `workspace-member-permissions`
- Updated `docs/project/self-hosted-commercial-baseline.md` with manual account management, bootstrap admin boundary, role boundaries, and out-of-scope SaaS/SSO/OAuth/billing/Marketplace flows.

## Validation

Commands run:

```text
python -m uv run pytest tests/db/test_migrations.py tests/db/test_schema.py tests/api/test_auth_api.py tests/api/test_team_api.py -q
python -m uv run pytest tests/api/test_imports.py tests/api/test_import_job_status_api.py tests/api/test_decisions_api.py tests/api/test_governance.py tests/api/test_drift_api.py tests/api/test_query_api.py tests/api/test_timeline_dashboard_api.py -q
pnpm --filter @decisionatlas/api test -- auth-route.test.ts imports-route.test.ts team-route.test.ts
pnpm --filter @decisionatlas/web test -- auth-session-flow.test.tsx private-repo-access-panel.test.tsx team-management-panel.test.tsx governance-page.test.tsx review-page.test.tsx workspace-dashboard.test.tsx
pnpm --filter @decisionatlas/api typecheck
pnpm --filter @decisionatlas/web typecheck
openspec validate team-account-workspace-permissions --type change --strict
openspec validate --all --strict
```

Observed results:

- Engine auth/team/schema tests: `10 passed`.
- Engine business API regression tests: `51 passed`.
- API route tests: `15 passed`.
- Web role/team surface tests: `32 passed`.
- API and Web TypeScript checks: passed.
- OpenSpec strict validation: `45 passed, 0 failed`.

## Current State

- `team-account-workspace-permissions` is implemented, validated, synced to main specs, and archived.
- Branch `feature/team-self-hosted-permissions` contains the team self-hosted permission baseline work.
- Two unrelated untracked files remain intentionally outside the commit set: `codex-history-repair.skill` and `decisionatlas-harsh-review_20260514.md`.

## Follow-Up

- Next recommended OpenSpec change: `multi-git-source-token-import`.
- After that: `collaborative-review-audit-trail`, then `offline-self-hosted-release-package`.
- Keep billing, hosted multi-tenancy, Marketplace, self-service OAuth, and SSO deferred until the self-hosted team product loop is stable.
