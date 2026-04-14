## Context

DecisionAtlas has already crossed the line from a single-user public-repo tool into the first platformized model:

- workspaces are becoming owner-scoped
- repository identity is separate from access source
- GitHub App installation can already bind a repository and drive webhook sync

The next missing piece is private repository access. Right now the product can describe that private access must be owner-authorized, but it does not yet define the concrete contract for:

- how an owner registers a credential-bearing access source
- how private repo import resolves through that source
- how a workspace remains reusable without storing secrets on the workspace itself
- how the product explains “repo exists, but you do not currently have an authorized access path”

This slice needs to stay narrower than full login/roles. It should establish private-repo authorization and credential reference handling, while assuming a current owner scope has already been resolved by the surrounding product context.

## Goals / Non-Goals

**Goals:**

- Define owner-scoped credential-bearing access sources for private repositories.
- Keep repository identity, workspace identity, and credential material separate.
- Define import/reuse/sync resolution for private repositories inside the current owner scope.
- Define clear product outcomes for missing credential setup, unauthorized access, and access-source mismatch.
- Preserve the current public-repo baseline while allowing private-repo support to layer in cleanly.

**Non-Goals:**

- Building full login, session, or membership systems.
- Implementing every possible provider beyond the GitHub-focused access model already in use.
- Designing encrypted secret storage internals in exhaustive detail.
- Cross-owner workspace sharing for private repositories.
- Reworking why, drift, or review semantics beyond access gating and outcome messaging.

## Decisions

### 1. Private repository access is always mediated by an owner-scoped access source

Private repositories must never be imported through an implicit global path. The current owner scope must resolve an authorized access source before import, lookup reuse, or incremental sync can proceed.

Rationale:

- private access is meaningless without an owner boundary
- the same repository may be accessible to one owner scope and unavailable to another
- this keeps private-repo behavior aligned with the platform-foundation model instead of introducing a side path

Alternative considered: allow a direct “repo + token” import request that bypasses stored access sources. Rejected because it hides authorization semantics inside one-off requests and makes reuse/sync behavior inconsistent.

### 2. Workspaces store access-source references, not raw credential material

Imported workspaces should record which access source they are bound to, but they should not store plaintext secrets or become the long-term container for credential material.

Practical shape:

```text
OwnerScope
  -> RepositoryAccessSource
       -> type = github_app_installation | github_token
       -> credential_ref / installation_ref
       -> allowed repo or repo scope

Workspace
  -> repo_identity
  -> owner_scope
  -> bound_access_source_id
```

Rationale:

- credentials may rotate without changing workspace identity
- multiple workspaces can share one authorized source inside a scope
- future secret storage can evolve without forcing workspace migrations

Alternative considered: copy the token or credential blob onto each workspace at import time. Rejected because it multiplies sensitive state and makes revocation harder.

### 3. Credential handling uses references and status, not secret echoing

The product should represent private access sources through labels and status:

- source type
- display label
- authorization status
- repository reachability status

It should not echo token values, secret fragments beyond minimal diagnostics, or provider payloads into normal workspace surfaces.

Rationale:

- reduces accidental leakage into logs, API payloads, and UI
- gives the product enough information to guide users
- matches the existing readiness-surface pattern

Alternative considered: expose detailed provider credential metadata everywhere for debugging. Rejected because the debugging value is low relative to the leakage risk.

### 4. Live analysis for private repos should fail honestly before import starts

When a private repository cannot be reached through the current owner scope's authorized access source, the product should return an explicit credential-required or unauthorized-access outcome instead of collapsing into generic repository-not-found or network failure.

Rationale:

- users need to know whether the repo is invalid, unreachable, or simply not authorized
- this keeps failure classes legible as the platform expands
- it prevents “try again later” style ambiguity for what is actually an authorization setup issue

Alternative considered: map all private access failures into existing repository failure categories. Rejected because it weakens the product's operator guidance at exactly the point where setup complexity increases.

### 5. Private repo reuse and incremental sync must preserve the original bound source unless deliberately re-bound

If a workspace was imported through a bound access source, later reuse and incremental sync should use that same source by default. Rebinding should be an explicit operation.

Rationale:

- avoids silent changes in trust and permission path
- keeps webhook/manual sync semantics coherent
- makes auditability easier once role enforcement arrives

Alternative considered: always resolve the “best available” access source on each sync. Rejected because it makes provenance unstable and can hide accidental permission escalation.

## Risks / Trade-offs

- [Credential model grows before auth exists] → Keep this slice owner-scoped and assume current owner resolution is provided externally; do not pull login into this change.
- [Too much implementation detail in a spec-first slice] → Define access-source reference behavior and product outcomes, but defer secret-storage internals to implementation choices.
- [PAT-only support may age poorly] → Model credential-bearing access sources generically enough that GitHub App and token variants fit under the same abstraction.
- [Private repo failures could still be confusing] → Add explicit credential-required and unauthorized-access outcome language in live-analysis specs.
- [Rebinding rules might feel strict] → Prefer explicit rebind over implicit source switching because provenance and security are more important than hidden convenience.

## Migration Plan

1. Add the private-repo and credential-handling contract in OpenSpec.
2. Introduce owner-scoped access-source persistence that can reference GitHub App installations and token-backed private access.
3. Update import and lookup paths so private repositories resolve through an authorized source before job creation.
4. Preserve current public/manual behavior as the baseline when no private access source is needed.
5. Layer login/roles later on top of this contract so action permission enforcement does not need to redesign repository access again.

## Open Questions

- Should the first private credential-bearing source be limited to GitHub PAT-style access, or should installation-backed private access and token-backed private access land together?
- Should one access source be allowed to cover all repositories visible to the owner, or should the product start with explicit per-repository binding?
- What minimum diagnostic detail is safe to expose when a credential is present but no longer valid?
