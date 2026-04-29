## 1. Plan Baseline

- [x] 1.1 Update `docs/plans/2026-04-29-decisionatlas-next-master-plan.md` so the current-state section reflects the actual Stage 3 starting baseline: latest pushed commit, `v0.3.0-rc.1` tag state, completed Stages 0-2, and active Stage 3 change.
- [x] 1.2 Add a short Stage 3 status note to the plan explaining that this change productizes existing lookup/sync primitives rather than starting a new architecture track.

## 2. Backend Reuse And Sync Contract

- [x] 2.1 Audit import lookup/start behavior for owner-scoped existing workspace detection, cross-scope isolation, access-source labeling, and active job reporting.
- [x] 2.2 Ensure repository lookup returns stable product fields for existing workspace slug, latest import state, latest sync origin/time, active queued/running job, last import summary, access-source status, and `can_incremental_sync`.
- [x] 2.3 Ensure import start re-checks active queued/running jobs and returns a bounded conflict/actionable state instead of blindly enqueuing an avoidable duplicate repeat run.
- [x] 2.4 Add or update engine/API tests for existing workspace reuse, cross-scope non-leakage, incremental sync availability, active import duplicate protection, and access-source-aware repeat-run state.

## 3. Product Surfaces

- [x] 3.1 Update the live analysis form so repeat repository lookup clearly presents open-existing, incremental-sync, and full-rerun choices before any new import starts.
- [x] 3.2 Make active import state route users to the existing workspace/job and disable or warn against duplicate repeat-run actions.
- [x] 3.3 Update dashboard/imported readiness surfaces to show latest sync time, sync origin, active sync/import state, recent sync history, and last import summary without duplicating local heuristics.
- [x] 3.4 Update i18n copy so incremental sync and full re-analysis are visibly distinct in English and Chinese.
- [x] 3.5 Add or update web tests for repeat-run choices, active import disabling/routing, dashboard sync state, and private/GitHub App access-source labels.

## 4. Documentation

- [x] 4.1 Update quick start guidance for repeat repository analysis: when to open existing, when to incremental sync, and when to full rerun.
- [x] 4.2 Update FAQ/operator guidance for duplicate running imports, access-source requirements, and expected sync provenance labels.
- [x] 4.3 Record any product-copy decisions or limitations discovered during implementation in the relevant plan or release documentation.

## 5. Validation

- [x] 5.1 Run targeted engine/API tests covering imports, import job status, dashboard summary, and access-source behavior.
- [x] 5.2 Run targeted web tests covering live analysis, workspace dashboard, imported readiness, and related route proxies.
- [x] 5.3 Run OpenSpec validation for this change and `openspec validate --all --strict`.
- [x] 5.4 Run the project validation gate that is practical in the local environment and record any skipped external/live-GitHub checks explicitly.
