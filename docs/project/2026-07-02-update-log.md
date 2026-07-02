# 2026-07-02 Update Log

## streamline-workspace-interaction-flow

### Implemented

- Added a current/target interaction-flow plan at `docs/plans/2026-07-02-decisionatlas-interaction-flow-optimization-plan.md`.
- Added role-aware homepage next actions for admin, reviewer, viewer, and operator workflows.
- Made repository import a visible guided flow on the homepage while keeping execution controls in the admin/advanced area.
- Split global operations and workspace workflow navigation more clearly in the sidebar.
- Added active workspace context banners to dashboard, review, search, timeline, drift, and decision detail pages.
- Strengthened decision detail as the cross-view object hub with next actions back to review, search, timeline, drift, and evidence.
- Reframed Evidence Center around release/operator questions: guardrail, benchmark comparison, hosted readiness, release evidence, and missing evidence next actions.
- Added/updated unit and browser smoke coverage for homepage import guidance, Evidence Center readiness flow, workspace context, and review/search-to-decision-detail continuity.

### Validation

- `pnpm --filter @decisionatlas/web test`: 20 test files passed, 78 tests passed.
- `pnpm --filter @decisionatlas/web typecheck`: passed.
- `pnpm --filter @decisionatlas/web exec playwright test mimo-ui-smoke.spec.ts --config playwright.config.ts --reporter=line`: 8 browser smoke tests passed against local engine/API/web smoke stack.
- `openspec validate streamline-workspace-interaction-flow --type change --strict`: passed.

### Notes

- Browser smoke required clearing local proxy environment variables for localhost checks because `all_proxy=http://127.0.0.1:7890` caused false 502/connection failures against local services.
- Playwright selectors were scoped to real `main` content to avoid matching Next streaming hidden payload markup.
