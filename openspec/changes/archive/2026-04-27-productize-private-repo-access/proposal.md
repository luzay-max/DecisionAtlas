## Why

Private repository access already exists as an engine/API capability, but it is not exposed as a safe product flow. After login, scope switching, and GitHub App setup were productized, the next blocker is letting an admin configure private-repository access inside the current owner scope without turning the product into a full secret-management system.

## What Changes

- Add an admin-facing private repository access setup surface for the current owner scope.
- Let admins bind a repository to a reusable token-backed GitHub access source through the existing private-access binding API.
- Show the resulting access-source label, authorization status, workspace slug, and next actions after binding.
- Keep the authenticated session scope as the authority; do not expose a typed owner-scope override.
- Preserve explicit credential-required and authorization-failure guidance in live analysis and imported workspace surfaces.
- Keep full secret vault, OAuth token exchange, rotation history UI, and member-management flows out of scope.

## Capabilities

### New Capabilities
- `private-repo-access-product-flow`: Admin-facing product flow for configuring token-backed private repository access in the current owner scope.

### Modified Capabilities
- `private-repo-access-and-credential-handling`: Clarify that credential-backed access sources must be manageable through a bounded product surface without exposing raw credential material after submission.
- `live-repository-analysis`: Extend the product-facing live analysis surface so private repository setup can happen before reuse or import.
- `login-roles-and-workspace-scoping`: Clarify that private-access management is an admin-only action in the current owner scope.
- `imported-workspace-readiness-surface`: Ensure imported workspace readiness surfaces continue to display private access-source status and details.

## Impact

- Web app: API client, admin setup component, home/live analysis integration, tests.
- API gateway: private-access proxy coverage and session-cookie forwarding assertions.
- Engine/API: no new storage model expected; reuse existing `github_token_access_sources`, workspace access-source binding, and private-access validation paths.
- Specs: add product-flow requirements and tighten existing private access, live analysis, role, and readiness contracts.
