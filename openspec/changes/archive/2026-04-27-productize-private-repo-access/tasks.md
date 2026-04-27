## 1. Private Access Client And Gateway

- [x] 1.1 Add typed web API client support for `/imports/github/private-access/bind`.
- [x] 1.2 Strengthen API gateway test coverage so private-access binding forwards the authenticated session cookie and keeps owner scope session-derived.

## 2. Product UI

- [x] 2.1 Add an admin-only private repository access panel that shows current owner scope, accepts repository/token/source metadata, and does not echo token material after submit.
- [x] 2.2 Integrate the private access panel into the advanced live-analysis/admin surface beside existing GitHub App setup.
- [x] 2.3 Show successful binding results with access-source label, authorization status/detail, workspace slug, and next action links.
- [x] 2.4 Show non-admin users a permission boundary instead of credential submission controls.

## 3. Access State And Readiness

- [x] 3.1 Preserve private repository credential-required and authorization-failure guidance in live analysis.
- [x] 3.2 Ensure imported workspace readiness surfaces continue to display token-backed access-source status and detail without exposing credentials.

## 4. Tests And Validation

- [x] 4.1 Add web component tests for successful private binding, failed binding, non-admin gating, and token non-echo behavior.
- [x] 4.2 Run targeted API/web tests for private access, live analysis, and home integration.
- [x] 4.3 Run the canonical pre-release validation script.
