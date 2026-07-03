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

## project-completion-taskbook

### Implemented

- Added `docs/plans/2026-07-03-decisionatlas-completion-taskbook.md` as the current execution taskbook.
- Mapped 2026-05-08 and 2026-05-09 plan lines to `complete`, `partial`, `missing`, and `not-now` states.
- Listed next OpenSpec candidates in priority order: `imported-workspace-core-loop-rehearsal`, `multi-repo-live-diagnosis-rotation`, `release-rehearsal-one-command-evidence`, `review-audit-ux-hardening`, and `external-customer-host-rehearsal-v2`.
- Added OpenSpec requirements for maintaining the completion taskbook and making final roadmap updates reference it.

### Validation

- `openspec validate project-completion-taskbook --type change --strict`: passed.
- `openspec validate --all --strict`: passed after synchronization.

### Notes

- The taskbook does not claim final completion. It explicitly keeps real imported workspace core-loop proof and multi-repo live diagnosis as remaining high-priority work.

## imported-workspace-core-loop-rehearsal

### Implemented

- Added `scripts/ci/collect_imported_workspace_core_loop.py` to collect setup/reuse, dashboard, review, why-search, drift, and guardrail lane evidence for an imported workspace.
- Added `services/engine/tests/ci/test_imported_workspace_core_loop.py` covering clean, partial, missing workspace, and compact Markdown behavior.
- Added `apps/web/tests-e2e/imported-workspace-core-loop.spec.ts` to create or reuse a real public GitHub workspace for `pallets/flask` and walk dashboard, review, why-search, drift, and evidence pages in a browser.
- Added `docs/project/imported-workspace-core-loop-rehearsal.md` with collector and browser run commands plus evidence boundaries.
- Updated the completion taskbook to show that imported core-loop evidence exists, while multi-repo live diagnosis remains the next higher-priority gap.

### Validation

- `python -m pytest services/engine/tests/ci/test_imported_workspace_core_loop.py -q`: 4 tests passed.
- `pnpm --filter @decisionatlas/web exec playwright test imported-workspace-core-loop.spec.ts --config playwright.config.ts --reporter=line`: 1 browser test passed.
- `python scripts\ci\collect_imported_workspace_core_loop.py --repo pallets/flask --workspace-slug github-pallets-flask --why-question "why is this imported workspace interesting" --output-json .tmp\imported-workspace-core-loop-rehearsal.json --output-markdown .tmp\imported-workspace-core-loop-rehearsal.md`: generated JSON/Markdown with expected `warning` status.

### Notes

- The `pallets/flask` imported workspace browser path is real, but why-search is mocked in the browser test for deterministic UI validation.
- The collector smoke intentionally preserved warnings: review queue was empty, why-search was `evidence_limited`, drift was warning, and guardrail was `not_provided`.
- This improves core-loop evidence but does not replace the next `multi-repo-live-diagnosis-rotation` work.
