## Why

The current product can import and incrementally sync repositories, but it still depends on manually initiated runs and public-access assumptions. v0.3 needs a first platform slice that turns repository updates into owner-scoped, continuously synchronized workspaces without prematurely bundling private-repository credential handling or full auth/roles work.

## What Changes

- Add GitHub App installation as a first-class repository access source that can be bound to an owner scope.
- Add installation-aware repository linking so a repository can be imported and reused through an owner-scoped GitHub App installation rather than only manual live analysis.
- Add webhook-driven incremental sync so qualifying GitHub events can enqueue `since_last_sync` imports for the correct imported workspace.
- Expose clearer sync-history and latest-sync state so product surfaces can explain whether a workspace is current, syncing, or behind.
- Keep this slice scoped to GitHub App installation and webhook sync only; private repository credential UX and login/role enforcement remain follow-on slices.

## Capabilities

### New Capabilities
- `github-app-webhook-incremental-sync`: Installation-aware repository binding and webhook-triggered incremental sync for imported workspaces.

### Modified Capabilities
- `live-repository-analysis`: Live analysis and repository reuse must recognize owner-scoped GitHub App access sources and report installation-backed reuse context honestly.
- `workspace-reuse-and-incremental-sync`: Repository lookup, reuse, and incremental sync must support installation-backed workspaces and webhook-triggered sync state.
- `platform-foundation`: The platform model must become concrete enough to define installation binding, webhook ownership resolution, and action boundaries for this first v0.3 slice.

## Impact

- Engine import orchestration, GitHub integration, and workspace lookup flows
- Database models for owner-scoped access sources, installation bindings, and sync metadata
- API surfaces for installation-backed repository state and sync history
- Web product surfaces that present installation-backed workspace reuse and latest sync state
