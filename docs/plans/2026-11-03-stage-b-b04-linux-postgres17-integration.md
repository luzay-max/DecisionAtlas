# Stage B / B04 — Ubuntu and PostgreSQL 17 integration for merged schema

**2026-11-03 — Draft CI proof, not production rollout.** Base is the independently verified Stage A `main@2641989b443ca6633019fa7b713521be0ce5686d`. B01 #43, B02 #44 and B03 #45 remain Draft/unmerged; this branch is **not stacked** on any of them.

## Scope

Add a dedicated `.github/workflows/ci-ubuntu-postgres17.yml` workflow. On Engine/workflow changes, it starts an **isolated disposable** Ubuntu service database from `pgvector/pgvector:pg17`, enables the extension, installs the existing Engine dependencies, and runs the **current merged** 0001→0012 Alembic chain on PostgreSQL 17. It asserts:

- PostgreSQL server version >=17 with pgvector installed, a fresh database (guard against arbitrary existing DB), and exact Alembic head `0012_review_audit_events`.
- Existing workspace/Artifact/Decision/SourceRef/review_audit_events/drift_alerts schema remains functional.
- **No** #34 tables (`artifact_revisions`, `artifact_current_revisions`, `artifact_extraction_runs`) or `source_refs.artifact_revision_id`, because the maintainer has **not authorized** that migration.
- Synthetic public workspace and another owner-scoped workspace; one accepted Decision, a candidate, a SourceRef with an exact quote, and audit JSON records survive an Engine/database reconnect.
- Accepted-only lexical search returns only accepted evidence from the named workspace; cross-workspace hits and unreviewed candidates are absent.
- PostgreSQL enforces foreign keys and workspace slug uniqueness, including after deliberate attempted invalid writes/transaction rollback.

There are no real source imports, external providers, paid model calls, private data, migration/downgrade of any existing deployment, production credentials, backup files or retained database artifacts.

## Acceptance and limitations

The existing Windows all-tests CI remains authoritative for repository-level compatibility. The new workflow only proves a **fresh Ubuntu PostgreSQL 17 instance** at the current 0012 schema can migrate, persist and retrieve synthetic reviewed evidence. It does **not** prove existing production upgrades, load/performance, Windows/Linux runtime parity, authorization against a real multi-tenant deployment, or #34 migrations/SourceRef versioning. Integration runtimes and actual check results must be recorded from the **latest B04 PR head**; a green Windows workflow alone is insufficient.

**Merge gate:** CI on exact head, independent maintainer review, explicit merge authorization. No auto merge. B01/B02/B03 branches must be reconciled and retested if main changes first.
