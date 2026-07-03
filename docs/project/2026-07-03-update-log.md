# 2026-07-03 Update Log

## real-browser-workflow-rehearsal

### Implemented

- Added `apps/web/tests-e2e/real-browser-workflow-rehearsal.spec.ts`.
- The rehearsal starts from homepage onboarding, opens import controls like a human operator, checks a real public GitHub repository reference for `openai/openai-cookbook`, then walks demo workspace, review, why-search, drift, evidence, and team role separation.
- Added `docs/project/real-browser-workflow-rehearsal.md` with the local run command and evidence boundary.
- Added OpenSpec requirements for `real-browser-workflow-rehearsal` and updated workspace interaction, Mimo UI smoke, and live repository analysis specs.

### Validation

- `pnpm --filter @decisionatlas/web exec playwright test real-browser-workflow-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 1 passed.
- `pnpm --filter @decisionatlas/web exec playwright test mimo-ui-smoke.spec.ts team-self-hosted-rehearsal.spec.ts --config playwright.config.ts --reporter=line`: 9 passed.
- `pnpm --filter @decisionatlas/web test -- --run tests/home-page.test.tsx tests/team-management-panel.test.tsx`: 2 files passed, 3 tests passed.

### Notes

- The real GitHub repository reference is asserted in the browser flow, but import lookup is mocked for deterministic UI testing. Live import quality remains covered by benchmark/readiness evidence.
- Local proxy variables must be cleared or bypass localhost before Playwright starts smoke servers.
