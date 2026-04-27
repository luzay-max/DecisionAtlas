## Why

DecisionAtlas already has owner-scoped GitHub App installation binding and webhook-triggered sync mechanics, but users still cannot operate that path from the product. After login and scope switching are visible, the next productization slice should make GitHub App-backed repository access understandable and actionable inside the current owner scope.

## What Changes

- Add a GitHub App installation product surface for the current owner scope.
- Let admins bind a repository to an installation-backed access source from the web UI using the existing `/imports/github/installations/bind` API path.
- Show installation-backed access source state in live analysis and workspace surfaces so users can distinguish public/manual imports from GitHub App-backed workspaces.
- Keep webhook ingestion and sync provenance visible through existing workspace readiness and sync history surfaces.
- Keep private repository credential setup and full GitHub App OAuth/callback automation out of scope for this change.

## Capabilities

### New Capabilities
- `github-app-installation-product-flow`: Covers the user-facing installation setup, repository binding, current-scope ownership, and installation-backed workspace state.

### Modified Capabilities
- `github-app-webhook-incremental-sync`: Productizes the existing installation binding and webhook sync requirements into visible setup and status behavior.
- `workspace-reuse-and-incremental-sync`: Clarifies that installation-backed reuse and manual sync actions are presented through the current owner scope.
- `live-repository-analysis`: Clarifies that live analysis can bind or reuse installation-backed repository state from the product flow.
- `platform-foundation`: Clarifies that GitHub App installation setup is an admin-level owner-scoped product action.

## Impact

- Affected web areas: home/live analysis form, workspace dashboard/readiness surfaces, new GitHub App installation/binding panel, tests.
- Affected API areas: existing Fastify `/imports/github/installations/bind` proxy may need small response/error handling refinements.
- Affected engine areas: existing installation binding and webhook routes should be reused; no new access-source model is expected.
- Affected docs/specs: GitHub App installation product flow and v0.3 platform productization requirements.
