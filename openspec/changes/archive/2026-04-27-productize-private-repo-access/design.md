## Context

The engine already supports token-backed private repository access through owner-scoped `github_token_access_sources`, workspace access-source binding, authorization status summaries, and `/imports/github/private-access/bind`. The API gateway already proxies that route. The missing piece is productization: admins need a safe UI path to bind private access inside the current scope, while reviewers/viewers need clear non-management states.

This follows the same product shape as the GitHub App installation setup: browser UI uses the current session, the gateway forwards the session cookie, and the engine remains the source of truth for workspace binding and access-source status.

## Goals / Non-Goals

**Goals:**
- Add an admin-only private repository access setup panel.
- Use the existing private-access binding API instead of introducing a parallel backend model.
- Keep current owner scope implicit from the authenticated session.
- Show binding results using existing access-source fields so live analysis and workspace readiness remain consistent.
- Add tests for client behavior, role gating, and gateway session forwarding.

**Non-Goals:**
- No full secret vault UI.
- No OAuth or GitHub App token exchange.
- No credential rotation history.
- No member-management work.
- No new database migration unless implementation reveals a missing persistence field.

## Decisions

### Reuse the private-access binding API

The UI SHALL call the existing `/imports/github/private-access/bind` route through a typed web client. This keeps credential validation, source upsert, workspace binding, and authorization status in the engine.

Alternative considered: add a frontend-only lookup path or direct engine call. Rejected because it would bypass the gateway session boundary and duplicate access-source semantics.

### Keep owner scope session-derived

The setup panel SHALL display the current owner scope but SHALL NOT let users type `owner_scope`. The API gateway/engine continue resolving scope from the authenticated session or trusted local bootstrap behavior.

Alternative considered: expose an owner-scope field for operators. Rejected because it creates accidental cross-scope credential binding risk and conflicts with the login/scope model.

### Treat token as submit-only client state

The panel SHALL hold the token only in form state long enough to submit it and SHALL not render it back after success. Success surfaces access-source label, status, detail, and workspace slug instead of credential material.

Alternative considered: show saved token metadata. Rejected for this iteration because the storage model does not yet carry safe token metadata such as last-four, expiry, or fine-grained permissions.

### Use existing role gate components

The UI SHALL reuse `AdminOnly` / product session context for management controls. Non-admins can see that private-access setup requires admin rights without being offered credential submission controls.

Alternative considered: rely only on backend rejection. Rejected because the product should distinguish permission boundaries from missing setup.

## Risks / Trade-offs

- Credential entry in browser UI → Mitigate by avoiding persistence in local storage, not echoing the token, clearing token state after submission, and relying on HTTPS in hosted environments.
- Token-backed access is less operationally ideal than GitHub App installation → Mitigate by positioning it as a bounded private-access setup path and keeping GitHub App as the preferred scalable integration.
- Existing API may allow payload fields beyond the UI scope → Mitigate with client types/tests that omit owner-scope override and gateway tests that preserve session forwarding.
- Users may confuse source reference and repo → Mitigate by defaulting source reference to the repository and making custom source label optional.
