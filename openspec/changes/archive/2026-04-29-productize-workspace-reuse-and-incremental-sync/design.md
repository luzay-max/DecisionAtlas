## Context

Stage 0 through Stage 2 established the v0.3 release-candidate baseline, improved imported decision quality, and made imported why-search more reliable. The next practical bottleneck is repeat repository analysis: the codebase already has import lookup, owner-scoped workspace identity, `since_last_sync`, sync provenance, active job detection, dashboard readiness, and GitHub App/private access binding, but those pieces need to behave as one product decision flow.

The current implementation already exposes many of these primitives through `lookupGithubImport`, `startGithubImport`, import job status, dashboard summary, and imported readiness cards. This change should avoid a large rewrite and instead make the contract sharper across API, UI, tests, and docs.

## Goals / Non-Goals

**Goals:**

- Make the master plan current-state section accurate before Stage 3 implementation starts.
- Make repeat repository entry resolve to explicit owner-scoped choices: open existing, incremental sync, or full rerun.
- Keep sync provenance and active import state visible on dashboard/import surfaces.
- Prevent accidental duplicate queued/running imports where the product already knows an active job exists.
- Document repeat-run behavior for users and operators.

**Non-Goals:**

- Do not add a full job management console.
- Do not implement cancel/pause/resume controls.
- Do not merge workspaces across owner scopes.
- Do not change the accepted decision, why-search, or drift trust model.
- Do not require live GitHub credentials in default CI.

## Decisions

### Decision: Treat repository lookup as the repeat-run gate

The live analysis entry point should call repository lookup before starting a job and should preserve owner-scope isolation in that lookup. If an imported workspace already exists, the default form submit must not silently start a full import.

Alternative considered: allow submit to start full rerun and show a warning after the fact. That keeps the flow shorter but preserves the main failure mode: users spend time and compute on duplicate analysis before understanding that a workspace already exists.

### Decision: Keep the action model small and explicit

The product should expose exactly three repeat-run actions for now:

- open existing workspace
- sync since the last successful import
- run full re-analysis

Alternative considered: expose advanced controls such as force re-index, re-extract only, cancel, and retry failed stage. Those may be useful later, but they would turn Stage 3 into job orchestration instead of workspace reuse productization.

### Decision: Surface active job state through existing summaries first

Dashboard and readiness views should reuse import job summary fields and readiness state rather than inventing a separate sync model. The UI can show latest sync origin/time, active job origin, recent sync history, and last import summary from the existing backend contract.

Alternative considered: add a dedicated sync dashboard endpoint. That may become useful when job controls exist, but it is unnecessary for this stage and risks duplicating dashboard/readiness logic.

### Decision: Use bounded prevention for duplicate active imports

If lookup or start-import detects a queued/running job for the same owner-scoped workspace, the product should disable or warn against duplicate import actions. Backend behavior should remain authoritative so direct API calls cannot create avoidable duplicates when the active state is known.

Alternative considered: rely only on UI disabling. That is cheaper but brittle because API clients and race conditions can bypass the UI.

## Risks / Trade-offs

- Active job detection may be stale between lookup and click -> re-check at start-import time and return a bounded conflict/actionable state.
- Reuse UI may become too noisy for first-time users -> only show the action card after lookup finds an existing workspace or access-source-specific state.
- Full rerun still has legitimate use cases -> do not remove it; label it clearly as a heavier re-analysis path.
- Owner-scope isolation mistakes could leak private workspace existence -> preserve current owner-scoped lookup semantics and cover cross-scope negative tests.
- Docs can drift from product copy -> update quick start/FAQ in the same change and include repeat-run validation in tasks.
