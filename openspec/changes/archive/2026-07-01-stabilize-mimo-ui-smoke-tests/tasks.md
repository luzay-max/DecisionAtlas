## 1. Unit Test Stabilization

- [x] 1.1 Mock `next/navigation` pathname behavior in review, drift, and timeline page-content tests where needed.
- [x] 1.2 Mock `GlobalSidebar` in review, drift, and timeline page-content tests so isolated unit tests do not require `ThemeProvider`.
- [x] 1.3 Run targeted Vitest coverage for review, drift, and timeline page-content tests.

## 2. Browser Smoke Coverage

- [x] 2.1 Add `apps/web/tests-e2e/mimo-ui-smoke.spec.ts` covering homepage onboarding, quick actions, settings, evidence, 404 recovery, and demo workspace navigation.
- [x] 2.2 Restore/verify local workspace dependency links required by the smoke webServer path.
- [x] 2.3 Run at least one successful Playwright browser smoke against the local Web/API/Engine smoke stack.
- [x] 2.4 Record proxy and dependency caveats discovered during smoke execution.

## 3. Governance And Evidence

- [x] 3.1 Run `openspec validate stabilize-mimo-ui-smoke-tests --type change --strict` and `openspec validate --all --strict`.
- [x] 3.2 Run or reuse a random public GitHub repository evidence check so this change remains attached to real-repo validation habits.
- [x] 3.3 Run governance guardrail and record the resulting state.
- [x] 3.4 Add a 2026-07-01 update log entry with commands, pass/fail states, limitations, and evidence paths.

## 4. Handoff

- [x] 4.1 Sync `mimo-ui-smoke-coverage` delta spec into main specs before archive.
- [x] 4.2 Archive `stabilize-mimo-ui-smoke-tests`.
- [ ] 4.3 Commit, push `origin/mimo`, and check CI status when network is available.
