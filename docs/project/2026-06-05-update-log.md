# 2026-06-05 Update Log

## Test Discovery Stabilization

- Added OpenSpec change `stabilize-engine-test-discovery` to formalize engine pytest discovery boundaries and scratch-output hygiene.
- Constrained engine pytest discovery to `services/engine/tests/` via `services/engine/pyproject.toml`.
- Updated the release checklist to keep temporary debugging scripts, generated local reports, and ad hoc validation artifacts in `.tmp/` or another ignored scratch location.
- Verified `uv run pytest --collect-only -q` from `services/engine/` collects only the canonical test suite and ignores root-level scratch `test_*.py` files.
- Moved existing untracked local scratch files into `.tmp/local-scratch/2026-06-05/` so they remain available locally without polluting Git status or pytest discovery.

## Validation

- `python -m uv run pytest --collect-only -q` from `services/engine/`: `247 tests collected`
- `python -m uv run pytest -q` from `services/engine/`: `247 passed`
- `pnpm typecheck`: passed
- `openspec validate stabilize-engine-test-discovery --type change --strict`: passed

## Notes

- Existing untracked local scratch files were intentionally preserved under ignored `.tmp/` storage and not committed.
- Browser/Chrome-based UI verification was not required for this configuration-only change; it remains required for the next UI-facing self-hosted/team workflow changes.

## Team Self-Hosted Workflow Rehearsal

- Added OpenSpec change `self-hosted-team-workflow-rehearsal` to make the small-team self-hosted account/permission workflow measurable with browser/operator evidence.
- Added Playwright rehearsal `apps/web/tests-e2e/team-self-hosted-rehearsal.spec.ts` covering admin team-management visibility, UI account creation for reviewer/viewer, and non-admin permission messaging.
- Added client-side session token persistence so browser login survives route changes and subsequent API calls use `x-decisionatlas-session-token`.
- Updated self-hosted readiness and delivery rehearsal docs to require the team workflow browser rehearsal for clean Team Self-hosted account/permission readiness claims.
- Added `@decisionatlas/web` `e2e` script so browser rehearsal commands use the Node Playwright package consistently.
- Selected real public GitHub repository `fastapi/fastapi` for optional live benchmark evidence. The generated reports `.tmp/team-rehearsal-fastapi-live-report.json` and `.tmp/team-rehearsal-fastapi-live-report.md` recorded `missing_workspace` / `operator_setup`, meaning the repository exists but had not been imported into the local rehearsal workspace before benchmark validation.
- Governance protocol after archive returned advisory `pause` because code changes no longer had an active OpenSpec change after `self-hosted-team-workflow-rehearsal` was archived; OpenSpec strict validation passed and the archived change is preserved as the implementation context.

## Public GitHub Import Rehearsal

- Added OpenSpec change `public-github-import-rehearsal` to close the gap between selecting `fastapi/fastapi` as live benchmark input and actually importing or reusing `github-fastapi-fastapi` before benchmark validation.
- Added `scripts/ci/rehearse_public_github_import.py` to perform public GitHub lookup/import/reuse through existing product APIs and generate `.tmp/public-github-import-rehearsal.json` plus `.tmp/public-github-import-rehearsal.md`.
- Added offline tests for rehearsal outcome classification: reused workspace, created import job, local-stack failure, and operator-guided access requirement.
- Updated self-hosted delivery rehearsal guidance so live public-repository benchmark claims require import/reuse proof with `benchmark_ready: true`; selected-but-not-imported repositories remain non-pass setup evidence.
