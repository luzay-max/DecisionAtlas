## Why

DecisionAtlas now has local login, bootstrap session recovery, role gates, self-hosted delivery evidence, and a team self-hosted product direction, but it still lacks the account and workspace permission loop needed for real small-team use. The next priority is to let a self-hosted administrator create users, assign roles, bind users to workspaces, and make reviewer/viewer collaboration safe before expanding more Git provider support.

## What Changes

- Add administrator-managed team accounts for self-hosted deployments.
- Add workspace-level member permissions so users only see and act on authorized workspaces.
- Preserve the existing local bootstrap admin path for development and first-run recovery.
- Enforce admin/reviewer/viewer permissions in both backend APIs and frontend product surfaces.
- Make viewer role read-only: viewers can inspect decisions, why-search, drift state, and evidence, but cannot import repositories, submit credentials, review candidate decisions, or mutate governance rules.
- Make reviewer role review-capable but not account/token-management capable.
- Keep self-service signup, password reset email, SSO/OIDC/SAML, SaaS multi-tenancy, and Marketplace/OAuth out of scope.

## Capabilities

### New Capabilities

- `team-account-management`: Administrator-managed user lifecycle for self-hosted teams, including create, disable, reset password, and assign roles.
- `workspace-member-permissions`: Workspace-level visibility and action permissions for admin, reviewer, and viewer members.

### Modified Capabilities

- `login-roles-and-workspace-scoping`: Extends the existing login, role, and owner-scope model to support administrator-created team users and workspace-level authorization while preserving bootstrap local mode.

## Impact

- Engine auth repository, auth/session APIs, and database models or migrations for account status and workspace membership.
- API auth forwarding and permission checks for workspace, import, review, drift, governance, and private-access routes.
- Web account-management UI, workspace permission UI, role-gated navigation, and read-only viewer surfaces.
- Tests for admin/reviewer/viewer permissions across engine, API, and web.
- Documentation updates for self-hosted administrator setup and team permission boundaries.
