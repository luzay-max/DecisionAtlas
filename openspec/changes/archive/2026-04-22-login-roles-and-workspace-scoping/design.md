## Context

The current platform model now distinguishes:

- repository identity
- access source
- owner-scoped workspace ownership

But product actions are still effectively open to any caller that can hit the route. The codebase has no durable actor model, no session-backed owner-scope resolution, and no role enforcement around review, drift, or sync actions.

That leaves the platform in an unstable middle state:

```text
owner scope exists in data
but actor identity does not exist in product flow
```

This change closes that gap. It turns owner scope from a modeling concept into an enforced runtime boundary.

## Goals / Non-Goals

**Goals:**

- Introduce a minimal login-backed actor model for the product.
- Define how the current owner scope is resolved for each request.
- Define the initial role model for imported-workspace actions.
- Enforce workspace visibility and write actions through owner-scope membership.
- Preserve the current single-user local developer baseline with a bootstrap path.

**Non-Goals:**

- SAML, OAuth marketplace integrations, or enterprise SSO.
- Fine-grained per-route ACLs beyond the product-action matrix.
- Cross-owner workspace sharing.
- Billing, seat management, or org administration UX beyond the minimum needed to support roles.
- Reworking repository-access source logic introduced in earlier v0.3 slices.

## Decisions

### 1. Start with session-backed application identity, not provider sprawl

The first implementation should introduce a DecisionAtlas application identity and session boundary. External identity providers can be added later, but the runtime model should be:

```text
request
  -> authenticated actor
      -> current owner scope
          -> role in that scope
              -> allowed product actions
```

Rationale:

- the platform needs actor identity now, regardless of eventual login provider
- local and self-hosted setups need a workable bootstrap path
- this avoids blocking role enforcement on a larger auth-provider decision

Alternative considered: defer all login work until GitHub auth or org SSO exists. Rejected because the platform already has owner-scoped data and now needs runtime enforcement.

Concrete first-release shape:

- local application accounts
- server-side session cookie
- password-based or bootstrap-admin login for local/self-hosted use

This is intentionally narrower than “full auth strategy.” It gives the platform a durable actor/session model without coupling v0.3 to an external provider decision.

### 2. Roles are assigned per owner scope, not globally

The role boundary should live on the membership between actor and owner scope, not on the actor alone.

Initial roles:

- `viewer`
- `reviewer`
- `admin`

Rationale:

- the same user may have different permissions in different scopes
- it fits the platform-foundation action model
- it avoids baking global admin assumptions into workspace access

Proposed action matrix:

```text
Action                Viewer   Reviewer   Admin
-----------------------------------------------
View workspace          yes       yes       yes
Run import / rerun       no        no       yes
Incremental sync         no        no       yes
Review candidates        no       yes       yes
Accept / reject          no       yes       yes
Evaluate drift           no       yes       yes
Manage access source     no        no       yes
Manage members           no        no       yes
```

Alternative considered: collapse reviewer and admin into one editor role. Rejected because credential and membership management are materially more privileged than decision review.

### 3. Owner scope must be explicit in product state, with a safe default bootstrap

The product needs one current owner scope per request/session. For the first slice:

- local single-user mode can auto-resolve to a bootstrap default scope
- multi-scope mode requires the actor to select or persist a current scope

Rationale:

- preserves current local developer ergonomics
- avoids breaking existing imported workspaces
- lets platform behavior move forward without pretending all users share one global scope

Alternative considered: infer scope from the repository or workspace alone. Rejected because it fails on cross-scope repo duplication and makes “list my workspaces” ambiguous.

Concrete first-release shape:

- the session stores `current_owner_scope_id`
- the product exposes an explicit scope-switch action
- APIs derive current scope from authenticated session state rather than trusting arbitrary caller-supplied scope identifiers

This keeps the first implementation simple and prevents accidental cross-scope reads caused by inconsistent frontend parameters.

### 4. Workspace visibility is enforced through owner scope first, then workspace lookup

All workspace reads should conceptually resolve as:

```text
actor
  -> scope membership
      -> workspace inside scope
```

not:

```text
workspace slug
  -> maybe actor can see it
```

Rationale:

- avoids leaking workspace existence across scopes
- aligns with the existing owner-scoped workspace model
- keeps dashboard, search, timeline, review, and drift consistent

Alternative considered: retain global slug-based lookup and add soft filtering later. Rejected because it is too easy to leak existence through lookup responses.

### 5. Existing imported-workspace flows should become actor-aware without changing their product meaning

The point of this slice is enforcement, not reinventing the imported lane. Existing actions should remain recognizable:

- open existing workspace
- incremental sync
- review candidates
- ask why
- evaluate drift

What changes is the gate in front of them.

Rationale:

- reduces product churn
- limits the implementation blast radius
- makes regression testing against current real-repo flows easier

### 6. System-triggered actions are not authenticated-user actions

Not every action in the platform should require a user session. The first implementation must distinguish:

- interactive actions:
  - dashboard
  - search
  - import/rerun buttons
  - review
  - drift evaluation
- system actions:
  - webhook-triggered sync
  - background import execution
  - access-source-driven automation

System actions should derive authority from:

- a bound access source
- an existing workspace binding
- an internal trusted execution path

not from an interactive browser session.

Rationale:

- keeps the new login model from breaking GitHub App webhook sync
- prevents accidental coupling between job execution and user sessions
- matches the platform-foundation distinction between product action authority and raw route entrypoints

Alternative considered: force all actions through an actor context. Rejected because webhook and job-runner flows are real system actions, not user clicks.

### 7. Bootstrap migration must preserve the current local baseline

The first implementation must explicitly preserve the current single-user product loop. Existing local data should migrate into:

- one bootstrap local actor
- one bootstrap owner scope
- one admin membership connecting them

Rationale:

- avoids breaking existing imported workspaces and demo flows
- keeps `start-real-stack` and current local release validation useful
- lets v0.3 auth land incrementally instead of as a flag day rewrite

Alternative considered: require manual user and scope creation during migration. Rejected because it would add avoidable operational friction to the current single-user baseline.

## Risks / Trade-offs

- [Auth scope gets overdesigned] -> Keep the first implementation to session identity, owner-scope membership, and three roles.
- [Single-user dev flow breaks] -> Keep a bootstrap admin/scope path so local startup still works without manual provisioning.
- [Role checks become route-by-route drift] -> Centralize permission checks around product actions instead of ad hoc controller conditionals.
- [Workspace visibility leaks through legacy lookups] -> Require owner-scope resolution before workspace lookup in dashboard, search, and live-analysis entry points.
- [Future external auth provider choice changes details] -> Treat provider choice as an adapter around the same actor/session/scope model.
- [Webhook sync breaks under auth enforcement] -> Treat webhook and job-runner flows as system-authorized execution paths, not browser-session actions.
- [Scope selection becomes a hidden source of bugs] -> Resolve current scope from session state and make scope switching an explicit product action.

## Migration Plan

1. Add actor, owner-scope membership, and role persistence.
2. Backfill a bootstrap local actor/admin membership for the current single-user baseline.
3. Add request/session actor resolution.
4. Update imported-lane APIs to require authenticated actor + resolved owner scope.
5. Enforce product-action permissions on import, sync, review, accept, and drift endpoints.
6. Preserve webhook/job execution through trusted system-action paths that do not depend on browser sessions.
7. Update frontend state to carry current scope and handle unauthorized/forbidden outcomes honestly.

Rollback direction:

- keep owner-scope data intact
- fall back to bootstrap local admin mode if session enforcement must be relaxed temporarily

## Open Questions

- Should the first login implementation use password-based local auth, magic links, or a developer-only bootstrap token flow?
- Should scope selection be explicit in the UI from the first release, or hidden while only one scope exists?
- Do accepted-decision actions and candidate-screening actions need separate reviewer sub-roles later, or is one reviewer role enough for now?
- Should API responses expose “not in scope” and “forbidden in scope” as distinct product-facing error classes from the first implementation?
