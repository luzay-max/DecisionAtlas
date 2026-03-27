## Context

DecisionAtlas already reuses imported workspaces by `repo_url`, and the backend already supports `full` and `since_last_sync` import modes. The gap is product semantics: users are still funneled into a default "run live analysis" action even when the repository already has a workspace and a successful import history. During implementation, this also exposed a bug where `since_last_sync` could compare naive database timestamps against GitHub's offset-aware timestamps.

## Goals / Non-Goals

**Goals:**
- Make workspace reuse explicit before launching a live import.
- Expose incremental sync as a first-class user action when a successful prior import exists.
- Prevent duplicate reruns when a job is already queued or running.
- Normalize `since_last_sync` timestamps so incremental sync is safe to execute.

**Non-Goals:**
- Add account-owned workspaces or workspace sharing.
- Add import cancellation.
- Add GitHub transport retries or network backoff in this change.
- Redesign the imported workspace dashboard itself.

## Decisions

### Add a lightweight lookup endpoint instead of overloading import submission
The engine and API proxy expose a dedicated repo lookup route that returns workspace existence, latest import, and incremental-sync availability. This keeps import submission simple and avoids starting work just to discover reuse state.

Alternative considered:
- Infer reuse only after calling `/imports/github`.
  Rejected because it still queues work before the UI can present a choice.

### Keep reuse controls in the live-analysis form
The existing entry point already owns repo input and redirect behavior, so the reuse choices belong there. This minimizes navigation churn and lets the user make a decision before a background job is created.

Alternative considered:
- Redirect users first, then ask on the workspace page.
  Rejected because it still feels like analysis has already started.

### Treat datetime normalization as part of the same user-facing flow
Incremental sync is not credible unless the `since_last_sync` path is safe. The fix belongs in `GitHubClient` so all import modes share normalized UTC-aware timestamps.

Alternative considered:
- Normalize timestamps only in `run_github_import`.
  Rejected because GitHubClient owns the boundary where external API timestamps are compared.

## Risks / Trade-offs

- **Lookup adds one more network round-trip before import** → Keep it lightweight and debounce it from the client.
- **Users may still choose full rerun too often** → Preserve full rerun, but visually frame reuse and incremental sync as the normal path.
- **Queued/running detection is only as fresh as the latest import job** → Return latest job state directly and disable rerun when the latest job is active.
- **Datetime normalization does not address other import fragility** → Leave GitHub retry/backoff for the next change rather than widening scope here.
