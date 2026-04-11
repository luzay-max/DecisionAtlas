## Context

DecisionAtlas already supports imported workspaces, repository reuse, and manual incremental sync, but all of that still assumes an operator starts the flow explicitly from the product. The v0.3 platform-foundation change established the missing boundaries: workspaces belong to an owner scope, repository access sources are distinct from repository identity, and sync/review actions must be expressed as product permissions rather than ad hoc route behavior.

This change is the first implementation slice on top of that model. It needs to make GitHub App installation concrete enough to support owner-scoped repository binding and webhook-triggered incremental sync, while keeping private-repository credential UX, user login, and full role enforcement out of scope for now.

The current codebase already has:
- live repository analysis and imported-workspace reuse flows
- `since_last_sync` incremental import behavior
- imported readiness and sync-related UI messaging
- lightweight real-repo benchmark cases and pre-release validation

The missing piece is a repository update path that does not rely on a user manually re-entering the repo every time something changes.

## Goals / Non-Goals

**Goals:**
- Bind a GitHub App installation to an owner scope and treat it as a first-class repository access source.
- Allow imported workspaces to record that they are backed by a GitHub App installation rather than only anonymous/public access.
- Accept GitHub webhook events, resolve them into the correct owner-scoped workspace, and enqueue incremental sync when appropriate.
- Expose enough latest-sync and sync-history state for product surfaces to tell whether a workspace is current, syncing, or stale.
- Preserve current public-repo manual import behavior as a baseline path.

**Non-Goals:**
- Full private-repository credential management UX.
- User login, role assignment, or enforcement beyond the owner/action model already defined.
- A generic multi-provider webhook/event framework.
- Rebuilding the import pipeline itself; this slice should reuse existing incremental import mechanics.
- Requiring live GitHub App infrastructure for local demo mode when public/manual import is sufficient.

## Decisions

### 1. Treat GitHub App installation as an owner-scoped access-source record
We will model installation-backed access as an access-source instance attached to an owner scope, not as a separate workspace type. That keeps repository identity stable while letting the same repo exist in different owner scopes with different access sources.

Why this over a global installation-to-repo map:
- It preserves the platform-foundation rule that workspace ownership is explicit.
- It avoids leaking reusable workspaces across owner scopes.
- It leaves room for future non-App credential sources without changing repository identity rules.

Alternative considered:
- Global installation mapping keyed only by GitHub repo.
  Rejected because it collapses ownership and access-source concerns back into a shared global workspace model.

### 2. Reuse the existing incremental import path for webhook sync
Webhook processing should resolve the target workspace and enqueue the same `since_last_sync` import behavior already used by manual incremental sync, instead of introducing a second sync engine.

Why:
- Existing normalization and filtering behavior already has regression coverage.
- It keeps this slice focused on trigger and ownership resolution rather than rewriting import semantics.
- It makes webhook sync and manual sync easier to explain and debug because they converge on the same job model.

Alternative considered:
- A dedicated webhook import pipeline.
  Rejected because it would duplicate filtering, status handling, and failure modes.

### 3. Scope webhook handling to a bounded set of sync-relevant GitHub events
Webhook ingestion should start with the smallest event set that materially updates imported workspaces, such as pull-request or repository events already relevant to the current importer inputs.

Why:
- It keeps event resolution understandable during the first slice.
- It avoids building a broad event bus before ownership and sync semantics are proven.
- It reduces accidental import storms or ambiguous triggers.

Alternative considered:
- Subscribe to many GitHub App events from day one.
  Rejected because it creates debugging and rate-control problems before product value is proven.

### 4. Persist sync provenance and latest-sync summary with the workspace/import history
Product surfaces need to distinguish manual rerun, manual incremental sync, and webhook-triggered sync. The workspace/import model should therefore expose latest sync origin, last successful sync time, active sync state, and a bounded recent-history view.

Why:
- Without provenance, “workspace is syncing” is too vague for product decisions.
- Sync history is the user-facing proof that webhook incremental sync is working.
- The same state can support dashboard, search, and future workspace-management views.

Alternative considered:
- Keep sync provenance only in logs.
  Rejected because product surfaces would still need to infer state from low-level job records.

### 5. Keep auth/roles as documented future enforcement, not implemented coupling in this slice
This slice should respect owner scope and action boundaries in its model and API shape, but it should not block on full auth/roles implementation.

Why:
- GitHub App + webhook sync is the highest-value next product slice.
- Forcing auth/roles into the same change would expand scope substantially.
- The platform-foundation change already captured the policy model; this slice can be built so later auth enforcement plugs in cleanly.

Alternative considered:
- Gate GitHub App work on full login/roles first.
  Rejected because it would delay the most product-visible platform capability.

## Risks / Trade-offs

- **[Risk] Webhook ownership resolution is underspecified** → Mitigation: require installation-to-owner binding and repository-to-workspace resolution to succeed before enqueueing sync; otherwise record a clear ignored-event outcome.
- **[Risk] Duplicate or bursty webhooks trigger too many imports** → Mitigation: dedupe or coalesce pending syncs per workspace and reuse existing active-job checks.
- **[Risk] Public/manual import and installation-backed import diverge in behavior** → Mitigation: force both paths through the same repository identity and incremental import code where possible.
- **[Risk] This slice accidentally commits to final auth semantics** → Mitigation: describe permissions in terms of actions and owner scope only; defer user/session enforcement to the later auth slice.
- **[Risk] Product state becomes too implementation-specific** → Mitigation: expose latest-sync summaries and recommended actions, not raw webhook internals.

## Migration Plan

1. Add owner-scoped installation/access-source records and workspace linkage without breaking current public/manual workspace behavior.
2. Backfill existing imported workspaces so they remain usable with a default/manual access-source posture.
3. Introduce GitHub App installation binding and webhook ingestion behind a bounded first-slice path.
4. Expose sync provenance and latest-sync state in APIs and UI surfaces.
5. Validate with current pre-release checks, lightweight benchmark fixtures, and at least one live imported workspace path that proves webhook-triggered incremental sync does not regress manual sync.

Rollback strategy:
- Disable webhook-triggered enqueueing while preserving installation records and manual import paths.
- Fall back to manual incremental sync without deleting existing imported workspaces.

## Open Questions

- Which exact GitHub webhook event set is the minimal useful first slice?
- Should installation-backed sync provenance live directly on the workspace summary, or only on import-job history with a computed latest state?
- How much recent sync history should product surfaces show before workspace-management exists?
- Do we need an explicit “installation no longer has access” product state in this slice, or can that wait for private-repo/access management follow-up?
