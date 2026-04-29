## Why

DecisionAtlas already has repository lookup, owner-scoped imported workspaces, sync provenance, and incremental import primitives, but the product path still needs a tighter repeat-run contract so users do not accidentally start duplicate full imports. Stage 3 should turn those primitives into an explicit workspace reuse decision flow before the v0.4 value work grows on top of it.

## What Changes

- Update the master plan current-state section so it reflects the actual post-v0.3 baseline before Stage 3 begins.
- Tighten live repository analysis so repository lookup clearly leads to one of three actions: open existing workspace, sync since the last successful import, or run a full re-analysis.
- Make imported workspace summaries show latest sync time, sync origin, active/running import state, and last import summary in a way dashboard and validation surfaces can reuse.
- Warn or prevent duplicate queued/running imports for the same owner-scoped workspace before starting another repeat run.
- Clarify quick start and FAQ guidance for repeat repository analysis, incremental sync, and full rerun behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `workspace-reuse-and-incremental-sync`: Strengthen owner-scoped lookup, explicit next actions, duplicate active import handling, and sync provenance requirements.
- `live-repository-analysis`: Require the live analysis entry flow to surface reuse/sync/rerun choices before starting another import.
- `imported-workspace-readiness-surface`: Require dashboard/readiness summaries to expose active sync/import state and repeat-run next actions consistently.

## Impact

- Affected web surfaces: `apps/web/components/home/live-analysis-form.tsx`, imported readiness/dashboard components, i18n copy, and related tests.
- Affected API/engine areas: import lookup/start endpoints, import job repository/service behavior, dashboard summary/readiness generation, and import job status tests.
- Affected docs: `docs/plans/2026-04-29-decisionatlas-next-master-plan.md`, quick start, FAQ, and repeat-run/operator guidance.
