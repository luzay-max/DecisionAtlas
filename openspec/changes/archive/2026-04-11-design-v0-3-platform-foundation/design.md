## Context

DecisionAtlas currently behaves like a high-quality single-operator product loop:

- repositories can be imported
- imported workspaces can be reopened or incrementally synced
- accepted decisions can power why-search and drift
- the imported lane has release-quality documentation and lightweight benchmark coverage

That baseline is strong enough that the next phase is no longer about local quality slices. The next phase is platformization:

- GitHub App installation
- private repository support
- login and roles
- multi-workspace scoping

The risk is that each of those features could be added independently and accidentally produce conflicting ownership rules. Today the model is effectively global: a repository maps to a workspace, and reuse/sync logic assumes one shared imported workspace identity. That model will break as soon as multiple users, organizations, or private credentials enter the system.

The current codebase reflects that global assumption directly:

- `Workspace` currently stores only `slug`, `name`, and `repo_url`
- workspace lookup is global via `get_by_repo_url`
- import APIs do not carry an owner, actor, or access-source identity
- import/review/drift actions are effectively available to whoever can hit the route

That means v0.3 needs a design pass before feature implementation, not just a backlog ordering.

## Goals / Non-Goals

**Goals:**

- Define the ownership model for users, organizations, repositories, credentials, and workspaces.
- Define how repository access sources map into workspace creation and reuse.
- Define the action-permission surface for import, review, acceptance, drift evaluation, and rerun flows.
- Establish a migration path from the current global imported-workspace model to an ownership-aware model.
- Reduce ambiguity before GitHub App, private repository support, and login work begins.

**Non-Goals:**

- Implementing GitHub App installs or webhook handlers.
- Implementing login screens or role enforcement.
- Implementing secret storage or encrypted credential management.
- Implementing multi-tenant billing or SaaS tenancy isolation.
- Reworking why/drift/indexing behavior unrelated to platform boundaries.

## Decisions

### 1. Introduce an explicit owner scope above workspaces

Future imported workspaces should belong to an owner scope, where the owner can be either:

- an individual user
- an organization/team container

The key decision is that repository-to-workspace mapping stops being globally unique and becomes unique within an owner scope.

Rationale:

- a public repo may be imported by different users for different purposes
- a private repo cannot safely be treated as a global shared object
- organization installs and user-scoped credentials need one common abstraction

Alternative considered: keep one global workspace per repo and add sharing later. Rejected because it makes private-repo ownership and per-tenant visibility too hard to retrofit.

Concrete shape:

```text
OwnerScope
  ├── type: user | organization
  ├── owner_key
  └── display metadata

Workspace
  ├── owner_scope_id
  ├── slug
  ├── repo_identity_id
  └── current readiness / import state
```

The important point is not the exact table names; it is that workspace identity becomes:

```text
owner scope + repository identity + workspace record
```

not:

```text
repository URL only
```

### 2. Separate repository identity from repository access source

The system should treat:

- the repository as the content identity
- the access source as the permission path used to reach it

Examples of access sources:

- anonymous public GitHub access
- user PAT or token
- GitHub App installation binding

Rationale:

- the same repo may be reachable through different access modes
- private-repo support requires more than “repo exists”; it requires “repo is reachable through this owner's allowed credential source”
- this keeps future credential migration from changing workspace meaning

Alternative considered: store credentials directly on workspaces. Rejected because it couples content ownership, access policy, and workspace identity too tightly.

Concrete shape:

```text
RepositoryIdentity
  ├── provider = github
  ├── canonical repo key = owner/repo
  └── metadata

RepositoryAccessSource
  ├── owner_scope_id
  ├── type = public | user_token | github_app_installation
  ├── credential/install reference
  └── allowed repositories or installation scope
```

This gives the platform one clean question to answer before import:

```text
Can this owner scope access this repository through an allowed source?
```

instead of mixing:

- whether the repo exists
- whether a workspace already exists
- whether the current actor is allowed to read it

inside one lookup path.

### 3. Reuse and incremental sync must become owner-aware

Existing repository lookup should remain, but workspace reuse must resolve inside the current owner scope first.

That means future lookup order becomes:

```text
owner scope
  -> repo identity
      -> existing workspace?
          -> reuse / incremental sync / full rerun
```

Rationale:

- preserves the good user experience of reuse
- avoids cross-user accidental workspace discovery
- keeps incremental sync semantics valid once multiple owners exist

Alternative considered: disable reuse for private repos at first. Rejected because it creates a worse product model right where platform features become more expensive.

Desired future flow:

```text
actor
  -> owner scope resolved
      -> repo lookup
          -> repository identity found
              -> authorized access source?
                  -> existing workspace in this scope?
                      -> open / sync / full rerun
```

This preserves the current good UX while eliminating future cross-tenant ambiguity.

### 4. Define action permissions around workspace lifecycle, not raw API routes

Permissions should be described in product actions first:

- import repository
- reuse existing workspace
- incremental sync
- review candidates
- accept/reject decisions
- evaluate drift
- view workspace

Rationale:

- product actions are stable across route changes
- easier to reason about reviewer/admin distinctions
- creates cleaner inputs for later API and UI enforcement

Alternative considered: define permissions only at route/controller level later. Rejected because it makes role discussions too implementation-specific and harder to audit.

Proposed minimum action matrix:

```text
Action                Viewer   Reviewer   Admin/Owner
-----------------------------------------------------
View workspace          ✓         ✓           ✓
Run import / rerun      -         -           ✓
Incremental sync        -         -           ✓
Review candidates       -         ✓           ✓
Accept/reject decision  -         ✓           ✓
Evaluate drift          -         ✓           ✓
Manage credentials      -         -           ✓
Manage members          -         -           ✓
```

This is intentionally a product-level matrix. Route-level permissions can map onto it later.

### 5. Slice the implementation by dependency, not by backlog label

The platform backlog items are tightly coupled, so implementation order should follow dependency edges:

```text
foundation
  -> github app + webhook sync
      -> private repo access
          -> login / roles / workspace scoping
              -> multi-workspace management
```

Why this order:

- GitHub App + webhook sync is the most direct product upgrade from the current imported lane
- private repo support depends on an access-source model
- roles and scoping depend on owner-scope semantics
- multi-workspace management depends on everything above

Alternative considered: start with login and roles first. Rejected because roles without repository-access and workspace-ownership semantics become placeholder auth, not platform behavior.

## Reference Model

```text
User ───────────────┐
                    │ member_of
                    ▼
                OwnerScope ─────────────┐
                    │                   │
                    │ owns              │ authorizes
                    ▼                   ▼
                Workspace         RepositoryAccessSource
                    │                   │
                    │ targets           │ reaches
                    ▼                   ▼
                RepositoryIdentity <────┘
                    │
                    ├── ImportJobs
                    ├── Decisions
                    ├── DriftAlerts
                    └── Search / Timeline / Dashboard state
```

Interpretation:

- `OwnerScope` is the durable tenant-like boundary for v0.3
- `RepositoryIdentity` is the logical repo object
- `RepositoryAccessSource` is how a scope is allowed to access that repo
- `Workspace` is where imported analysis state lives

## First Three Follow-on Slices

### Slice A: GitHub App installation and webhook-based incremental sync

Purpose:

- bind GitHub installation context to an owner scope
- authorize repository access through installation scope
- map webhook events to an existing workspace in that owner scope
- trigger incremental sync instead of blind full reimport

Not included:

- full role system
- generic multi-provider credential management

### Slice B: Private repository support and credential handling

Purpose:

- add non-public repository import through owner-authorized access sources
- define safer storage/reference for user-scoped credential material
- preserve the same workspace reuse rules inside an owner scope

Not included:

- full org member management
- cross-owner workspace sharing

### Slice C: Login, roles, and workspace scoping

Purpose:

- identify the acting user
- resolve the current owner scope
- enforce the product-action matrix
- scope dashboard/search/workspace access correctly

Not included:

- advanced org policy matrix
- billing or deep multi-tenant controls

## Risks / Trade-offs

- [Foundation feels abstract] → Keep this change tightly linked to the next three concrete v0.3 slices: GitHub App, private repo support, and roles.
- [Overdesign before implementation] → Limit the scope to ownership, access source, and permission boundaries; defer provider-specific details.
- [Migration complexity from current global workspaces] → Treat migration as explicit owner-scope backfill rather than hiding it in later implementation changes.
- [User vs organization ambiguity] → Use “owner scope” as the durable abstraction and allow user/organization to become variants of that model.
- [Public repo duplication across scopes] → Accept some duplication if needed; correctness of ownership matters more than premature deduplication.
- [GitHub App details distort the model too early] → Keep installation semantics represented as one access-source type, not the whole foundation.

## Migration Plan

1. Define the owner-scope, access-source, and action-permission contracts in OpenSpec.
2. Use those contracts as prerequisites for:
   - GitHub App installation design
   - private-repository credential handling
   - login / role enforcement
3. In later implementation changes, add data-model migration that can backfill existing imported workspaces into a default owner scope.
4. Preserve current release checks while the system is still single-user by resolving the default owner scope implicitly.
5. Only switch lookup/routing behavior to fully owner-aware mode once both owner resolution and access-source resolution exist.

Concrete migration direction:

```text
today:
  Workspace(repo_url) -> global

transition:
  Workspace(repo_url, owner_scope_id=default_local_owner)

future:
  Workspace(owner_scope_id, repo_identity_id, access via source)
```

## Validation Guardrails

The following checks must remain green throughout the first v0.3 slices:

- `pre-release.ps1`
- lightweight benchmark fixture validation
- live `browser-use` why benchmark cases
- imported workspace reuse behavior for existing public repos
- drift remains manually evaluable and conservative

These are not the full platform test suite, but they are the minimum guardrails that prevent v0.3 work from regressing the current imported-repo baseline.

## Open Questions

- Should the first owner scope implementation be user-only, with organization ownership added immediately after, or should both be designed into the first migration?
- Should reviewer/admin roles exist at the owner-scope level, workspace level, or both?
- How much of the GitHub App installation model should be represented as repository access source versus organization binding?
- Should imported public repositories remain shareable across scopes by default, or should every scope get its own logically separate workspace?
