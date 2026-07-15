# 2026-07-01 Update Log

## Stabilize Mimo UI Smoke Tests

- Active branch: `mimo`.
- OpenSpec change: `stabilize-mimo-ui-smoke-tests`.
- Purpose: stabilize Mimo/sidebar/onboarding UI tests and add browser smoke coverage for homepage, settings, evidence, 404 recovery, and demo workspace navigation.

## Implementation

- Updated page-content unit tests to isolate global sidebar/theme dependencies:
  - `apps/web/tests/review-page.test.tsx`
  - `apps/web/tests/drift-page.test.tsx`
  - `apps/web/tests/timeline-page.test.tsx`
- Added Mimo UI browser smoke:
  - `apps/web/tests-e2e/mimo-ui-smoke.spec.ts`
- Adjusted the demo workspace smoke assertion to verify the current `.global-sidebar` navigation links instead of the older `.demo-nav-link` selector.
- Restored local pnpm workspace dependency links needed by smoke execution:
  - `pnpm install --filter @decisionatlas/web...`
  - `pnpm install --filter @decisionatlas/api...`

## Validation

- `pnpm --filter @decisionatlas/web test -- review-page drift-page timeline-page`: `3 passed`, `14 tests passed`.
- `pnpm --filter @decisionatlas/web exec playwright test mimo-ui-smoke.spec.ts --config playwright.config.ts --reporter=line` with local proxy variables cleared: `7 passed`.
- `openspec validate stabilize-mimo-ui-smoke-tests --type change --strict`: valid.
- `openspec validate --all --strict`: `65 passed`, `0 failed`.
- `python scripts\governance\agent_guardrail.py --summary`: `caution`, diff check `pass`, drift report `drift_detected`.

## Real Stack And Browser Evidence

- Started the real stack with `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1`.
- Health checks after startup:
  - Web `http://127.0.0.1:3000`: `200`.
  - API `http://127.0.0.1:3001/health`: `{ "ok": true }`.
  - Engine `http://127.0.0.1:8000/health`: `{ "ok": true }`.
- Playwright Mimo UI smoke exercised real Chromium against local smoke Web/API/Engine services.

## Random Public GitHub Repository Evidence

- Selected repository: `browser-use/browser-use`.
- Command: `python scripts\ci\rehearse_public_github_import.py --repo-id browser-use --base-url http://127.0.0.1:3001 --wait --timeout-seconds 120 --poll-seconds 5 --output-json .tmp\mimo-ui-browser-use-public-github.json --output-markdown .tmp\mimo-ui-browser-use-public-github.md`.
- Evidence:
  - `.tmp/mimo-ui-browser-use-public-github.json`
  - `.tmp/mimo-ui-browser-use-public-github.md`
- Outcome: `reused`.
- Benchmark ready: `true`.
- Latest successful import: webhook incremental import, status `succeeded`.
- Current evidence summary: `67` reviewable decisions across PR/commit/issue sources.
- Limitation: this run reused an existing successful public repository workspace; it did not trigger a fresh full import.

## Environment Caveats

- Local proxy variables were set to `127.0.0.1:9` and caused GitHub API and Playwright webServer availability checks to fail or mis-detect local services.
- Reliable local browser smoke required clearing `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `GIT_HTTP_PROXY`, and `GIT_HTTPS_PROXY` for the command process while preserving `NO_PROXY=localhost,127.0.0.1,::1`.
- `apps/web` and `apps/api` package links were incomplete before running e2e; `@playwright/test` and `tsx` were not resolvable until pnpm workspace links were restored.
- Governance guardrail remained `caution`; its concrete recommendation to add navigation/pathname mocks was addressed by the passing Vitest suite, while historical-repeat signals remain advisory.

## GitHub Actions Node 24 Readiness

- OpenSpec change: `upgrade-github-actions-node24-readiness`.
- Purpose: remove CI release-readiness risk from GitHub Actions Node.js 20 action deprecation warnings while preserving the current validation scope.
- Updated `.github/workflows/ci.yml` action majors after checking current GitHub releases:
  - `actions/checkout@v7`
  - `actions/setup-node@v6`
  - `pnpm/action-setup@v6`
  - `actions/setup-python@v6`
  - `astral-sh/setup-uv@v8.2.0`
- Follow-up CI check showed `astral-sh/setup-uv` does not expose a moving `v8` tag, so the workflow pins the current concrete `v8.2.0` release instead.
- Kept the runner pinned to `windows-2025`; the workflow does not rely on `windows-latest` alias migration behavior.
- GitHub Actions verification:
  - Failed run `28500541409`: `astral-sh/setup-uv@v8` could not be resolved.
  - Passing run `28500706278`: all validation steps passed after pinning `astral-sh/setup-uv@v8.2.0`.
  - The passing run no longer showed the previous Node.js 20 deprecation annotation in `gh run view`.
