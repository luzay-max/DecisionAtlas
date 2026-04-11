## Why

DecisionAtlas has finished the current release-quality loop for public imported repositories, but the next phase cannot safely jump straight into GitHub App installs, private repositories, or user roles without first defining ownership and permission boundaries. The platform foundation needs to be explicit now so the v0.3 features build on one coherent model instead of layering access, workspace, and sync logic ad hoc.

## What Changes

- Define the core v0.3 platform model for:
  - users and organizations
  - workspace ownership and visibility
  - repository access sources such as GitHub App installations and user-scoped credentials
  - action permissions for import, review, drift, and rerun flows
- Establish how live analysis, workspace reuse, and future incremental sync should behave once workspaces are no longer global single-user artifacts.
- Clarify the minimal platform surface required before implementing:
  - GitHub App auth
  - private repository support
  - login / reviewer-admin roles
  - multi-workspace management
- Keep this change design-first: define the contracts and migration boundaries without implementing the full platform feature set yet.

## Capabilities

### New Capabilities

- `platform-foundation`: Defines ownership, access, credential, and workspace-boundary requirements for v0.3 platform work.

### Modified Capabilities

- `live-repository-analysis`: Live analysis requirements change from an effectively global imported-workspace model to an ownership-aware and credential-aware model.
- `workspace-reuse-and-incremental-sync`: Existing workspace lookup and sync behavior must become scoped to the owning user or organization instead of assuming a single global workspace mapping.

## Impact

- Affected product model:
  - workspace ownership
  - repository access model
  - credential source model
  - permission boundaries for review and drift actions
- Affected future implementation areas:
  - GitHub App installation flow
  - private repository support
  - login / role model
  - multi-workspace management
- Likely affected systems in later implementation:
  - engine data model
  - API auth and routing
  - workspace lookup and import orchestration
  - dashboard/search scoping

This change is intentionally foundational and architectural. It defines the platform contracts that later v0.3 implementation changes will follow.
