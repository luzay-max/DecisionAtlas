## 1. Data Model And Auth Foundation

- [x] 1.1 Add account status fields needed for enabled/disabled users while preserving bootstrap actor compatibility.
- [x] 1.2 Add workspace membership storage or equivalent authorization mapping for user-to-workspace roles.
- [x] 1.3 Add migrations and migration tests for account status and workspace membership changes.
- [x] 1.4 Extend auth repository helpers for creating users, disabling users, resetting passwords, and resolving effective workspace roles.

## 2. Engine APIs And Authorization

- [x] 2.1 Add admin-only engine endpoints for listing, creating, disabling, resetting, and assigning roles to team accounts.
- [x] 2.2 Add admin-only engine endpoints for assigning and removing workspace members.
- [x] 2.3 Reject login and session recovery for disabled users, including previously issued session tokens.
- [x] 2.4 Enforce effective admin/reviewer/viewer permissions on import, sync, review, drift mutation, governance mutation, private access, and account-management routes.
- [x] 2.5 Preserve local bootstrap admin creation and mark bootstrap sessions clearly.

## 3. API Gateway

- [x] 3.1 Add API routes that forward account-management and workspace-member-management requests to the engine.
- [x] 3.2 Ensure API routes forward session cookies and do not accept typed owner-scope overrides for sensitive actions.
- [x] 3.3 Add API tests covering admin success, reviewer/viewer denial, disabled user denial, and session forwarding.

## 4. Web Product Surfaces

- [x] 4.1 Add an admin-only team/account management page or panel.
- [x] 4.2 Add workspace member assignment UI that shows current user, role, workspace, and permission boundary.
- [x] 4.3 Update existing action gates so viewers see read-only decision, why-search, drift status, timeline, and evidence surfaces without mutation controls.
- [x] 4.4 Update reviewer/admin surfaces so reviewers can review but cannot manage accounts, imports, tokens, or workspace membership.
- [x] 4.5 Add clear disabled/unauthorized/permission-required copy instead of showing missing-data states.

## 5. Tests

- [x] 5.1 Add engine tests for team account lifecycle and workspace permission enforcement.
- [x] 5.2 Add API tests for role-based forwarding and denial paths.
- [x] 5.3 Add web tests for admin account management, reviewer limitations, viewer read-only behavior, and bootstrap session visibility.
- [x] 5.4 Run targeted auth, workspace, review, drift, governance, and import tests.

## 6. Documentation

- [x] 6.1 Update self-hosted documentation with manual account creation, default bootstrap admin, and role boundaries.
- [x] 6.2 Update the team self-hosted plan or implementation notes with any changed assumptions.
- [x] 6.3 Document that signup, SSO, OAuth, SaaS billing, and Marketplace flows remain out of scope.

## 7. Validation

- [x] 7.1 Run `openspec validate team-account-workspace-permissions --type change --strict`.
- [x] 7.2 Run `openspec validate --all --strict`.
- [x] 7.3 Run the relevant pre-release or targeted test subset and record any non-clean states.
