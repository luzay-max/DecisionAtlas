## Why

GitHub App installation binding is now available as an admin/operator product flow, but the post-binding sync behavior is still hard to observe from the product. Stage 3 turns GitHub App-backed synchronization into an explainable operational surface so users and operators can tell whether a workspace is maintained by manual import, manual incremental sync, or webhook-triggered sync.

## What Changes

- Show GitHub App-backed workspace status and access-source context on workspace/import surfaces.
- Expose latest sync provenance using clear product labels for:
  - manual full import
  - manual incremental sync
  - webhook-triggered sync
  - installation-backed full/incremental sync
- Add a bounded recent sync history or latest sync event summary where the existing API/data model can support it.
- Distinguish webhook-triggered sync from manual sync in UI copy and operator documentation.
- Add operator guidance for configuring, validating, and troubleshooting GitHub App webhook sync.
- Add tests for GitHub App-backed lookup, dashboard sync provenance, and webhook origin rendering.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `github-app-webhook-incremental-sync`: Productize webhook/incremental sync provenance so GitHub App-backed workspaces expose sync origin and webhook-triggered state clearly.
- `github-app-installation-product-flow`: Extend the installation binding product flow to make the post-binding workspace state and sync operations observable.

## Impact

- Web UI: workspace dashboard, import/live-analysis surfaces, and any sync status copy that renders `sync_origin` or access-source metadata.
- API/engine contract: may expose existing latest import/sync metadata more consistently; schema changes should be minimal and backward compatible.
- Documentation: hosted/operator docs should include webhook configuration, validation steps, and troubleshooting notes.
- Tests: web component tests, API route tests, and targeted engine tests for sync provenance behavior.
- Non-goals: no full GitHub OAuth Marketplace install flow, no GitHub App permission automation, no complex job management console.
