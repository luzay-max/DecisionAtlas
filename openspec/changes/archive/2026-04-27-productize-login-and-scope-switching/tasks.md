## 1. Auth Session Product Surface

- [x] 1.1 Add a web auth/session client that uses existing Fastify `/auth/session`, `/auth/login`, and `/auth/scope` routes.
- [x] 1.2 Add a login page or login panel for non-bootstrap environments, including invalid-credential and login-required states.
- [x] 1.3 Preserve local bootstrap session recovery and show the bootstrap actor/scope in the product shell.

## 2. Scope Switcher And Navigation

- [x] 2.1 Add a persistent product-shell account/scope surface that shows actor, role, current owner scope, and available scopes.
- [x] 2.2 Add owner-scope switching UI that calls `/auth/scope`, refreshes session state, and updates scope-bound product state.
- [x] 2.3 Add scoped unavailable/not-found handling for workspace pages when the current scope cannot access the requested workspace.

## 3. Workspace Action Semantics

- [x] 3.1 Ensure workspace actions render according to current role: viewer, reviewer, and admin.
- [x] 3.2 Keep import/rerun/credential-management entry points admin-only while preserving review/drift behavior for reviewer.
- [x] 3.3 Keep demo and local developer flows working with auto-bootstrap enabled.

## 4. Tests And Validation

- [x] 4.1 Add API proxy tests for login/session/scope cookie behavior if existing coverage is incomplete.
- [x] 4.2 Add web tests for session recovery, login-required UI, visible current scope, scope switching, and scoped workspace unavailable state.
- [x] 4.3 Run targeted auth/scope tests plus the canonical pre-release validation.
