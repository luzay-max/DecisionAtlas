## Why

DecisionAtlas now has an owner-aware platform model and GitHub App-backed webhook sync, but private repository access is still undefined at the product and spec level. Without an explicit credential-handling slice, the system cannot safely move from public-repo-only workflows into owner-authorized private imports, reuse, and incremental sync.

## What Changes

- Introduce an explicit private-repository access and credential-handling capability for owner-scoped imports.
- Define how owner-authorized access sources for private repositories are registered, referenced, and selected without turning workspaces into credential containers.
- Extend live analysis and workspace reuse behavior so private repositories can be imported, reopened, and incrementally synced only through an allowed owner-scoped access source.
- Clarify product-facing outcomes when a private repository is unreachable, unauthorized, or requires credential setup before import can proceed.

## Capabilities

### New Capabilities
- `private-repo-access-and-credential-handling`: Owner-scoped credential sources, private-repository authorization, and safe access-source resolution for imported workspaces.

### Modified Capabilities
- `platform-foundation`: Repository access sources and product permissions now need explicit private-repository credential rules.
- `live-repository-analysis`: Live analysis must expose private-repository credential requirements and failure states honestly.
- `workspace-reuse-and-incremental-sync`: Private-repository reuse and incremental sync must resolve through an authorized owner-scoped access source.

## Impact

- Engine data model for repository access sources and credential references
- Import and live-analysis APIs
- Workspace lookup and incremental sync resolution
- Product-facing imported readiness and failure messaging
- Future GitHub App, PAT, and owner-scope security work
