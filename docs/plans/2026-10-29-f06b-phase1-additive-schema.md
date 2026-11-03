# F06b Phase 1: expand-only revision schema (provisional implementation)

**2026-10-29 · Draft-only**. Base `main@8aa461f5`. Implements the first schema **proposal** described by RFC PR #33; it is not approval to change runtime import or reviewer data.

## Changes and invariants
- Alembic 0013 adds `artifact_revisions`, `artifact_current_revisions`, and `artifact_extraction_runs`; adds a **nullable** `source_refs.artifact_revision_id` FK.
- No changes to `ArtifactRepository`, `GitHubImporter`, `CandidateExtractionPipeline`, existing API serializers, extraction jobs, or review endpoints. All new tables are initially empty; the live import/extraction behavior stays unchanged.
- Old SourceRefs are **legacy_unbound** (NULL revision ID). Do not auto-backfill or reinterpret historical quotes.
- Schema constraints protect unique revision numbers/fingerprints per artifact, unique extractor claims, and **both** current-pointer and SourceRef revision-to-Artifact congruence via composite foreign keys. The SourceRef constraint accepts NULL revision IDs so legacy evidence remains unbound. Hash accuracy, snapshot immutability and concurrency ordering still require separately reviewed **future writer logic**.
- Downgrade refuses to delete populated revisions. No auto-prune of evidence history or private source bytes.
- Provisional capture fingerprint fields and retention policy are **not finalized**. Do not activate writers until RFC #33 is accepted.

## CI acceptance
- [ ] Alembic upgrade from 0012 with preexisting source references leaves all refs intact/unbound and creates empty new tables.
- [ ] SQLite foreign keys prevent both current pointers and SourceRefs from binding another Artifact's revision; positive bindings and nullable legacy refs remain valid.
- [ ] Constraints on revision number/fingerprint uniqueness and extraction identity work on SQLite.
- [ ] Existing Engine tests and full Windows CI pass on final head.
- [ ] **PostgreSQL 17 + pgvector** real-stack and **file-backed SQLite** local/desktop upgrade rehearsals, backup/restore, retention/security review and maintainer approval remain pending. MySQL is not an F06b-supported target.

## Dependencies and rollout
This PR is independent of unmerged PR #26/#28/#29/#30/#31/#32/#33 and modifies only additive DB schema, SQLAlchemy models and new tests. Schema correctness on CI SQLite is not evidence of a safe production upgrade. Execute the migration on a **copy** of representative data first; do not merge or activate features without explicit approval and the reviewed RFC.

**Proposed next work after approval:** F06b Phase 2 transaction-safe dual-write, then explicit legacy snapshot backfill without SourceRef relinking; Phase 3 read-version API and user-visible provenance; Phase 4 gated revision-keyed candidate-only re-extraction.


## Supported backend and future desktop scope (maintainer direction, 2026-11-03)

The maintainer confirmed PostgreSQL + pgvector as the server/full-stack database and SQLite as the lightweight local database, with a **possible future packaged desktop application**. MySQL support is explicitly deferred; do not advertise any MySQL migration as supported/validated.

Schema-only Phase 1 must be safe for **both** PostgreSQL and file-backed SQLite, not merely SQL compilation in SQLite in-memory mode:

- PostgreSQL 17 migration from 0012 with real \`source_refs\` data, new table/constraint/index validation, role privileges and representative backup/restore. Do not claim the composite FK behaves correctly on PostgreSQL until actually exercised.
- SQLite database-file migration from 0012 with old refs retained and \`artifact_revision_id IS NULL\`; measure the Alembic batch-recreate cost for large \`source_refs\` tables, available free disk space, rollback/restore and restart on a copy of realistic data.
- SQLite requires \`PRAGMA foreign_keys=ON\` **on every connection** for FK constraints to be enforced, including in the eventual packaged Engine. Current engine factory only sets \`busy_timeout\` once; the connection policy is a separate implementation task.
- For desktop planning, store user database/backups in a writable per-user data directory, not in application resources, and preserve them across upgrade/uninstall. A later packaging ADR must determine app shell/runtime, vector search fallback, credential store and user-data encryption.
- SQLite write serialization/short transactions, WAL/checkpoint and bounded busy-timeout must be tested; do **not** enable experimental pause/resume while Issue #36 worker-lock/lifecycle acceptance remains open.
- The migration's current \`server_default=sa.func.now()\` timestamps must be treated as database-local SQL time semantics until UTC normalization is specified. Local clock equality is **not** a reliable revision ordering policy.
- F06b canonical fingerprint, current-pointer CAS, immutable revision protections, snapshot retention/deletion, and extraction-worker claim lifecycle are still unresolved **RFC/ADR gates**. This prototype does not activate writers or backfill.

**Status:** Draft schema prototype; documentation change only. The database support decision does not approve this migration, merging #34, or distributing a desktop installer.


## F06b v1 ADR review gate: pointer generation and ABA (2026-11-03)

The current RFC #33 v1 architecture proposal requires an **explicit monotonic `generation`** on `artifact_current_revisions`, to compare-and-swap both `(revision_id, generation)`. Checking revision ID alone fails the A→B→A case: a concurrent writer can change the current snapshot away from revision A and back to A while an older capture is still in flight. An ID-only CAS would accept that stale capture.

**Current #34 schema does not include a pointer generation field.** Do not claim the prototype is concurrency-safe, do not activate dual-writes or call it approved. After RFC approval, review an additive migration/model change that introduces `generation` with a non-null initialized value and transactional increments on every pointer transition (including reuse of an earlier fingerprint), preserving the stable historical `artifact_revisions` rows. Cover fresh rows, concurrent pointer creation, A/B conflict, **A→B→A ABA**, duplicate imports and failure rollback on PostgreSQL + file-backed SQLite. Such an implementation change requires a separately reviewed exact-head CI and migration rehearsal.

This remains a **design note**, not an amendment to running migration or production logic. MySQL is out of the agreed support matrix.
