## Context

The backend already supports owner-scoped GitHub App installation records, installation-backed workspace binding, and webhook-triggered incremental sync. The Fastify API proxies `/imports/github/installations/bind`, and workspace/readiness payloads already carry access-source labels and sync provenance. The product gap is operational: admins cannot set up or understand GitHub App-backed repository access from the web surface.

This change follows the completed login/scope productization slice. It should use the current session's owner scope and role to present installation setup without adding a new identity provider, OAuth callback flow, or private token credential UI.

## Goals / Non-Goals

**Goals:**
- Add a minimal admin-facing GitHub App installation/binding surface.
- Reuse existing `/imports/github/installations/bind` and access-source payloads.
- Make installation-backed workspace state visible from live analysis and workspace surfaces.
- Preserve current public repository import and hosted demo flows.
- Keep webhook sync provenance visible when installation-backed sync occurs.

**Non-Goals:**
- Do not implement GitHub OAuth or an automated GitHub App callback exchange.
- Do not implement private repository token setup.
- Do not add organization/member management.
- Do not redesign the whole workspace directory.
- Do not introduce a separate installation database model beyond the existing one.

## Decisions

### 1. Productize the existing manual installation binding first

The first product surface will let an admin enter a repository and GitHub App installation id, optionally with account metadata, and bind it through the existing API proxy.

Rationale:
- Backend and API support already exist.
- This creates an operable path now, while a later OAuth/callback flow can automate installation id discovery.
- It is enough for hosted demo/operator validation of installation-backed workspaces.

Alternative considered: build the full GitHub App install/callback flow now. Rejected because it requires external app configuration, callback URL handling, and broader deployment secrets before the core product state is visible.

### 2. Keep binding scoped to the current session owner scope

The web UI should not ask the user to type `owner_scope`. The Fastify and engine routes should continue deriving scope from the authenticated session.

Rationale:
- The current scope switcher is the source of truth for owner context.
- Prevents accidental cross-scope binding from a form field.

Alternative considered: expose owner scope as an advanced form field. Rejected because it weakens the product boundary just added in the login/scope slice.

### 3. Treat installation-backed state as access-source metadata

Live analysis and workspace dashboard surfaces should reuse `access_source_type`, `access_source_label`, latest sync origin, and recent sync history instead of adding a parallel GitHub App-specific state model.

Rationale:
- The platform model already separates repository identity from access source.
- Private repo and token-backed sources can later use the same display pattern.

Alternative considered: add a dedicated GitHub App status widget independent of workspace/access-source state. Deferred because it would duplicate information and drift from the backend contract.

### 4. Keep admin-only controls explicit

Only admins should see installation binding controls. Reviewers/viewers may see the access-source state of a workspace they can view, but not mutate installation binding.

Rationale:
- Installation binding controls repository access and sync authority.
- This matches the platform permission model where access-source management is more privileged than review.

## Risks / Trade-offs

- [Manual installation id entry is less friendly than OAuth] -> Label the flow as an operator/admin setup path and keep full callback automation as a follow-up.
- [Users may bind the wrong repository to an installation] -> Show the target repo, current owner scope, and resulting access-source label after binding.
- [Webhook behavior is hard to observe without real GitHub delivery] -> Keep webhook provenance surfaced through existing latest/recent sync fields and cover binding behavior with deterministic tests.
- [Private repository expectations may leak into this slice] -> Keep private credential setup explicitly out of scope and route private access wording to the later private repo change.

## Migration Plan

1. Add web API client support for installation binding.
2. Add admin-only installation binding UI and integrate it with live analysis/workspace state.
3. Add tests for API proxy behavior and web binding/status states.
4. Run targeted tests plus canonical pre-release validation.

Rollback is straightforward: remove the web binding UI and client function while leaving existing backend installation and webhook routes in place.

## Open Questions

- What should the production GitHub App install URL be once the app slug is known?
- Should later OAuth/callback automation create a separate onboarding page or extend this admin setup panel?
- Do we need a workspace directory before installation-backed workspace discovery becomes comfortable for non-operator users?
