## 1. Current State Audit

- [x] 1.1 Audit engine lookup/import/bind paths for private access failure categories and access-source status updates.
- [x] 1.2 Audit API proxy schemas/tests for private-access binding, token omission, session-scope forwarding, and role behavior.
- [x] 1.3 Audit web surfaces that render token-backed state: live analysis, private access setup, workspace dashboard, imported readiness, and related tests.
- [x] 1.4 Identify current operator documentation gaps for token permissions, rotation, troubleshooting, and hosted-preview non-goals.

## 2. Engine and API Hardening

- [x] 2.1 Normalize private access failure categories for missing source, unauthorized/revoked token, repository not found, provider/network failure, and validation failure.
- [x] 2.2 Ensure token-backed bind/import/lookup responses include safe access-source label, authorization status, and bounded detail where available.
- [x] 2.3 Ensure raw token material is never returned in engine/API responses or reusable workspace/readiness summaries.
- [x] 2.4 Preserve current owner scope as session-derived authority and keep private access setup admin-only through API proxy behavior.

## 3. Product Surface Hardening

- [x] 3.1 Update live analysis lookup and private access setup UI to show actionable private access state and recovery copy.
- [x] 3.2 Update workspace dashboard and imported readiness surfaces to render token-backed label, status, and bounded detail consistently.
- [x] 3.3 Keep submitted token values out of success, error, and existing-workspace product rendering.
- [x] 3.4 Ensure non-admin private access setup remains unavailable or clearly disabled with current-scope role guidance.

## 4. Operator Documentation

- [x] 4.1 Update hosted/operator docs with recommended token permission boundary and rotation guidance.
- [x] 4.2 Document troubleshooting for missing source, unauthorized/revoked token, insufficient permissions, repository not found, provider/network failure, and stale status.
- [x] 4.3 Document deferred scope: no secret vault, no token rotation history UI, no GitHub OAuth/Marketplace private repo onboarding, and no live private credentials in default CI.

## 5. Tests

- [x] 5.1 Add or update engine tests for private access failure classification and no-token response behavior.
- [x] 5.2 Add or update API tests for private-access proxy behavior, token omission, role gates, and session-scope authority.
- [x] 5.3 Add or update web tests for private access setup, lookup, dashboard/readiness rendering, and non-admin behavior.
- [x] 5.4 Run targeted engine, API, and web tests covering private repository access hardening.

## 6. Final Validation

- [x] 6.1 Run relevant typechecks for changed packages.
- [x] 6.2 Run OpenSpec validation for `harden-private-repo-access-operations`.
- [x] 6.3 Record any deferred production hardening work discovered during implementation without expanding this change scope.
