# F06b Phase 1: expand-only revision schema (provisional implementation)

**2026-10-29 · Draft-only**. Base `main@8aa461f5`. Implements the first schema **proposal** described by RFC PR #33; it is not approval to change runtime import or reviewer data.

## Changes and invariants
- Alembic 0013 adds `artifact_revisions`, `artifact_current_revisions`, and `artifact_extraction_runs`; adds a **nullable** `source_refs.artifact_revision_id` FK.
- No changes to `ArtifactRepository`, `GitHubImporter`, `CandidateExtractionPipeline`, existing API serializers, extraction jobs, or review endpoints. All new tables are initially empty; the live import/extraction behavior stays unchanged.
- Old SourceRefs are **legacy_unbound** (NULL revision ID). Do not auto-backfill or reinterpret historical quotes.
- Schema constraints protect unique revision numbers/fingerprints per artifact, unique extractor claims, and cross-artifact current revision pointers. Other cross-field integrity (SourceRef artifact/revision congruence, hash accuracy, snapshot immutability, concurrency ordering) requires explicitly reviewed **future writer logic**.
- Downgrade refuses to delete populated revisions. No auto-prune of evidence history or private source bytes.
- Provisional capture fingerprint fields and retention policy are **not finalized**. Do not activate writers until RFC #33 is accepted.

## CI acceptance
- [ ] Alembic upgrade from 0012 with preexisting source references leaves all refs intact/unbound and creates empty new tables.
- [ ] Constraints on current pointer, revision number/fingerprint uniqueness and extraction identity work on SQLite.
- [ ] Existing Engine tests and full Windows CI pass on final head.
- [ ] Cross-backend MySQL migration, backup recovery, retention/security review and maintainer approval remain pending.

## Dependencies and rollout
This PR is independent of unmerged PR #26/#28/#29/#30/#31/#32/#33 and modifies only additive DB schema, SQLAlchemy models and new tests. Schema correctness on CI SQLite is not evidence of a safe production upgrade. Execute the migration on a **copy** of representative data first; do not merge or activate features without explicit approval and the reviewed RFC.

**Proposed next work after approval:** F06b Phase 2 transaction-safe dual-write, then explicit legacy snapshot backfill without SourceRef relinking; Phase 3 read-version API and user-visible provenance; Phase 4 gated revision-keyed candidate-only re-extraction.
