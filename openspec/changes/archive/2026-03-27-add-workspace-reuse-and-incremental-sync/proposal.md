## Why

Repeated real-repository analysis currently reuses the same workspace implicitly, but the product does not tell users when that is happening or offer a clear choice between opening existing results, syncing incrementally, and rerunning a full analysis. That creates avoidable model cost, confusing workspace semantics, and fragile repeat-run behavior.

## What Changes

- Add an explicit repository lookup flow before starting live analysis so the product can detect existing imported workspaces.
- Expose three user actions for existing imported workspaces: open existing workspace, sync since the last successful import, and rerun a full analysis.
- Prevent incremental sync from failing on naive-versus-aware datetime comparisons by normalizing `since_last_sync` timestamps before GitHub API filtering.
- Surface running-import state in the lookup response so the UI can discourage duplicate reruns.

## Capabilities

### New Capabilities
- `workspace-reuse-and-incremental-sync`: Covers repository lookup, explicit reuse controls, and user-facing incremental sync entry points for imported workspaces.

### Modified Capabilities
- `live-repository-analysis`: Live analysis now needs to expose whether a repository already has an imported workspace and whether incremental sync is available.
- `real-repository-outcomes`: Imported workspace entry semantics now need to distinguish opening existing results from rerunning or syncing the repository.

## Impact

- Engine import job orchestration and repo lookup path
- Engine imports API and API proxy routes
- Live analysis form UX and localized copy
- Import-related regression tests in engine, API, and web
