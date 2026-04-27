## Context

The platform backend already includes actors, owner scopes, memberships, sessions, role checks, workspace owner-scope fields, and API routes for login/session/scope switching. The Fastify API already proxies auth routes and stores the session token in a cookie. The missing piece is productization: the web UI does not yet make login state, current owner scope, or scope switching visible enough for users to understand workspace boundaries.

This change is the first v0.3 productization slice. It should turn existing auth and scope foundations into a usable product flow while preserving local demo behavior and avoiding GitHub App/private repo work.

## Goals / Non-Goals

**Goals:**
- Add a web login/session surface backed by the existing `/auth/*` routes.
- Show the current actor, role, and owner scope in the product shell.
- Allow switching between available owner scopes without losing the session.
- Keep scoped workspace navigation understandable when the same repository can exist under different scopes.
- Preserve local bootstrap behavior for demos and development.

**Non-Goals:**
- Do not implement GitHub App installation onboarding.
- Do not implement private repository credential setup.
- Do not add a full organization member-management UI.
- Do not introduce a new auth provider or OAuth flow.
- Do not redesign the whole app shell beyond the minimum needed for session and scope visibility.

## Decisions

### 1. Use the existing cookie-backed API proxy as the browser session boundary

The web app should call the Fastify API `/auth/session`, `/auth/login`, and `/auth/scope` endpoints. The browser should not manage the engine session header directly; Fastify remains responsible for translating the cookie into the engine session header.

Rationale:
- The API proxy already owns cookie setting and session header forwarding.
- Keeping this boundary avoids duplicating auth token handling in multiple frontend call sites.

Alternatives considered:
- Store the engine session token in local storage. Rejected because the API already provides safer cookie handling and direct token management would create an unnecessary second session surface.

### 2. Add a small session client instead of scattering auth fetches

The web app should centralize auth/session calls in a small client or hook that can be reused by navigation, login, and scope-switching UI.

Rationale:
- Session recovery, 401 handling, and scope switch refresh behavior should stay consistent across pages.
- This keeps follow-on GitHub App and private repo UI work from reinventing session handling.

Alternatives considered:
- Fetch `/auth/session` independently inside each page. Rejected because it would make scope state and error handling inconsistent.

### 3. Preserve local bootstrap as an explicit local mode

When `AUTO_BOOTSTRAP_AUTH` remains enabled in local/demo environments, the product should recover a bootstrap session without forcing a manual login. In non-bootstrap environments, unauthenticated users should see a login path and clear authentication-required state.

Rationale:
- The guided demo and local operator flows should keep working.
- Hosted/productized environments need a visible login path instead of invisible anonymous state.

Alternatives considered:
- Force login in all environments immediately. Rejected because it would make current demo/operator flows unnecessarily brittle.

### 4. Scope switching changes product context, not route identity by itself

Changing owner scope should refresh session context and scoped data, but it should not silently claim that the same workspace slug exists in the new scope. If the current page targets a workspace that is not visible in the new scope, the UI should show a scoped not-found/empty state and offer navigation to available workspaces.

Rationale:
- Workspace identity is scope-bound in the platform model.
- Silent cross-scope remapping would make permission boundaries harder to trust.

Alternatives considered:
- Automatically redirect to a same-repository workspace in the new scope. Deferred because that belongs with a richer workspace directory/search flow.

## Risks / Trade-offs

- [Existing local flows depend on auto bootstrap] -> Keep bootstrap recovery as a supported local path and test it separately from manual login.
- [Scope switching can strand a user on a workspace page] -> Show a clear scoped unavailable state and provide a route back to workspace navigation.
- [Frontend auth state can drift from cookie state] -> Refresh `/auth/session` after login and scope switch, and treat 401 as a logged-out state.
- [This may expose backend payload gaps] -> Add only small payload fields needed for display labels; defer member management and access-source UI to later changes.

## Migration Plan

1. Add frontend session client and UI around existing auth API routes.
2. Add minimal route/page states for login, logged-out, bootstrap local mode, and scoped workspace unavailable.
3. Add tests for login/session recovery, scope switch, and scoped navigation behavior.
4. Keep current local demo and pre-release checks passing.

Rollback is straightforward: remove the new web session UI and keep the backend auth routes in place.

## Open Questions

- Should the first login screen use only username/password for existing local actors, or should it also expose a bootstrap-admin entry in local mode?
- Should the first scope switch UI live in the top navigation or on a dedicated account/scope page?
- Do we need a minimal workspace directory in this change, or is scoped unavailable feedback enough for the first slice?
