# Stage B / B04 — Ubuntu and PostgreSQL 17 integration for merged schema

**2026-11-05 — Draft CI proof, not production rollout.** This PR has been reconciled to current `main@4c400018fbf24a8308c4d8176c340235b15bd130` (post-merge #49 security repair and #45 B03). B01 #43, B02 #44 and B03 #45 are merged; #49 is also merged. B04 remains an independent Draft and does not introduce #34 or production features.

## Scope

Add a dedicated `.github/workflows/ci-ubuntu-postgres17.yml` workflow. On Engine/workflow changes, it starts an **isolated disposable** Ubuntu service database from `pgvector/pgvector:pg17`, enables the extension, installs the existing Engine dependencies, and runs the **current merged** 0001→0012 Alembic chain on PostgreSQL 17. It asserts:

- PostgreSQL server version >=17 with pgvector installed, a fresh database (guard against arbitrary existing DB), and exact Alembic head `0012_review_audit_events`.
- Existing workspace/Artifact/Decision/SourceRef/review_audit_events/drift_alerts schema remains functional.
- **No** #34 tables (`artifact_revisions`, `artifact_current_revisions`, `artifact_extraction_runs`) or `source_refs.artifact_revision_id`, because that migration remains unapproved.
- Synthetic public workspace and another owner-scoped workspace; one accepted Decision, a candidate, a SourceRef with an exact quote, and audit JSON records survive an Engine/database reconnect.
- Accepted-only lexical search returns only accepted evidence from the named workspace; cross-workspace hits and unreviewed candidates are absent.
- PostgreSQL enforces foreign keys and workspace slug uniqueness, including after deliberate attempted invalid writes/transaction rollback.

There are no real source imports, external providers, paid model calls, private data, migration/downgrade of any existing deployment, production credentials, backup files or retained database artifacts.

## Base reconciliation and CI evidence

- Current main: `4c400018fbf24a8308c4d8176c340235b15bd130`.
- B04 candidate after base reconciliation: `f95009dc577c36aee1c1479b0f3a199beee698c3`; comparison is **5 ahead / 0 behind**, merge base exactly current main.
- The three B04 paths are isolated additions: the workflow, this plan and the PostgreSQL integration test. No B04 application-code changes are included.
- Previous B04 exact-head checks [#41596183044](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596183044) (Windows CI) and [#41596182326](https://github.com/luzay-max/DecisionAtlas/actions/runs/41596182326) (Ubuntu PostgreSQL 17) passed on the old base; they are historical and do not validate the new main.
- Updated exact-head Windows CI and PostgreSQL 17 workflow must both pass before this PR can be considered for approval.

## Acceptance and limitations

The existing Windows all-tests CI remains authoritative for repository-level compatibility. The new workflow only proves a **fresh Ubuntu PostgreSQL 17 instance** at the current 0012 schema can migrate, persist and retrieve synthetic reviewed evidence. It does **not** prove existing production upgrades, load/performance, Windows/Linux runtime parity, authorization against a real multi-tenant deployment, or #34 migrations/SourceRef versioning.

**Merge gate:** exact-head Windows CI SUCCESS, exact-head Ubuntu PostgreSQL 17 SUCCESS, independent maintainer review and explicit merge authorization. No auto merge. If main advances, reconcile and rerun exact-head CI. B04 remains Draft until separately approved.
