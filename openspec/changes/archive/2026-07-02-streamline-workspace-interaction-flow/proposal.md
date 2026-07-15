## Why

DecisionAtlas already has the main product pages, but the interaction flow still feels like an engineering console: users can reach many tools, yet the recommended next action is not always obvious. The next productization step is to reorganize the frontend around role, workspace, and task flow so admins, reviewers, viewers, and operators can complete their work quickly.

## What Changes

- Define a workspace-centered interaction model that keeps users anchored in the current workspace while moving between dashboard, review, search, timeline, drift, governance, and evidence.
- Introduce role-oriented landing behavior so admins, reviewers, viewers, and operators see the most relevant next action first.
- Convert repository import from a homepage advanced control into a clearer guided flow: connect source, validate access, start import or reuse workspace, monitor progress, then continue to review.
- Reframe Evidence as a productized evidence center for guardrail, benchmark, hosted readiness, release evidence, and audit history rather than a script reference page.
- Strengthen decision detail as the core object page linking summary, source evidence, review status, timeline, drift, and audit trail.
- Add a planning document that records the current flow, target flow, gaps versus common SaaS/GitLab/Jira/Linear interaction patterns, and implementation phases.

## Capabilities

### New Capabilities

- `workspace-interaction-flow`: Covers the expected role-aware, workspace-centered frontend interaction flow and navigation behavior.

### Modified Capabilities

- None.

## Impact

- `apps/web/app/**`
- `apps/web/components/navigation/global-sidebar.tsx`
- `apps/web/components/home/live-analysis-form.tsx`
- `apps/web/components/dashboard/workspace-dashboard-content.tsx`
- `apps/web/components/auth/**`
- `apps/web/app/evidence/page.tsx`
- `apps/web/components/review/**`
- Browser smoke and page interaction tests
- Planning documentation under `docs/plans/`
