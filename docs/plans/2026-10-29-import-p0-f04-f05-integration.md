# Integration gate — P0 + F04 + F05 GitHub import correctness

**Status:** Draft stacked integration PR, based on **unmerged PR #26 head** `8fa1e066`; not approved for merge.
**Date:** 2026-10-29
**Upstream:** PR #26 raw content credential isolation and progress transaction atomicity
**In this stack:** PR #30 fail-closed source coverage + PR #31 conservative UTC start-time overlap.

## Why use a stacked branch?
The three independent Draft PRs edit the same `github_client.py`, `import_jobs.py` and both test files. Separate green CIs cannot establish combined correctness, and they will conflict if merged in arbitrary order. This branch **integrates the behavior in code**, not just in an RFC or checklist.

## Implementation review
1. Base is exactly PR #26 head; it preserves authenticated GitHub Contents raw handling and rejects cross-host/token leaks and redirects.
2. F04 typed `GitHubIncompleteCoverageError` rejects incomplete pagination and tree truncation; importer cannot mark partial coverage as success.
3. F05 uses last *successful start* minus a bounded 5-minute UTC overlap for incremental scans, recording the effective query window and keeping failed runs out of successful anchors.
4. Progress callbacks remain uncommitted during import. F05's early `session.commit()` happens **before** the importer is constructed/writes artifacts, not inside the import callback.
5. New cross-feature regression artificially inserts an Artifact, reports import progress, then raises F04's typed error; ensure the job is failed with `incomplete_source_coverage` and no partial row is committed.

## Acceptance
- [ ] Latest-head Windows CI passes (Engine / API / Web / typecheck / MCP / offline regressions / Playwright).
- [ ] P0 credential isolation and progress rollback regressions remain green.
- [ ] F04 bounded HTTPX pagination/tree tests and failure classification remain green.
- [ ] F05 SQLite incremental time overlap and failed retry anchoring remain green.
- [ ] NEW integrated partial-write + progress + incomplete-coverage failure test passes.
- [ ] Human review of fail-closed large repo behavior, window policy, CI, and operational acceptance.


## Recovery boundary: committed import versus downstream indexing (2026-10-30)
The importer's verified source writes are committed after completing document collection. A failure **after that boundary** (e.g. indexing/extraction) marks the job failed but does **not** revert those committed Artifacts. This is not entire-job atomicity, and a failed job's `imported_count` should not be interpreted as the number of already committed source rows. Existing Artifact upserts keyed by source identity make retried captures idempotent; a retry uses the previous successful start-time overlap until a full job succeeds.

A new SQLite integration regression runs an import that commits one Artifact, intentionally fails downstream indexing, then retries. Expected: two failed jobs, one durable/upserted Artifact with a stable ID, both retries using the previous successful watermark, and explicit failed stage/category. This **characterizes** existing persistence behavior; it does not change the writer or promise cleanup of all other side effects. Real DB concurrency and private GitHub imports remain untested.

## Dependencies and merging
- This PR **targets the branch of Draft PR #26**, not `main`. Do not merge into the base branch without approval.
- After PR #26 is eventually approved and merged, explicitly rebase/retarget this integration PR onto `main`, rerun CI on the new head and reconcile standalone PRs #30/#31 (avoid duplicate merges).
- This does not merge any PR, does not rewrite `main`, and leaves #26/#30/#31 unchanged.
- Real private repo, provider pagination limit, hard 1000-result API boundaries, cross-workspace auth and worker cancellation need controlled end-to-end acceptance; the overlap is not a full exactly-once cursor protocol.

## P0 import pause/resume concurrency reproducers (issue #36, 2026-10-30)

**Added SQLite file-backed tests** in `services/engine/tests/test_import_pause_sqlite_concurrency.py`. These are not claims that pause/resume is implemented correctly:
- `test_paused_queued_job_cannot_be_overwritten_by_late_worker_start` is a **strict expected failure (xfail)** until worker start becomes a state-guarded claim. Current `mark_running` unconditionally changes `paused` to `running`.
- `test_completed_job_cannot_be_resurrected_by_duplicate_worker_start` is also **strict xfail** until a duplicate worker cannot move `succeeded` back to `running`.
- `test_uncommitted_artifact_write_blocks_separate_sqlite_pause_update` is a positive reproduction: an import-phase uncommitted SQLite Artifact writer causes a separate pause update to encounter a database lock under a deliberately short busy timeout. It cleans up the transaction and checks no partial source data or admin pause survived.

These tests validate a **risk**, not a safe end-to-end pause feature. Strict xfails should turn into normal passing tests when worker lifecycle code is changed; unexpected success must not go unnoticed. The production DB timeout is longer than the test's 150ms timeout, so a real UI may wait much longer. No change to the live worker scheduling, API, source import transaction, or pause-state machine is made here.

**Remaining acceptance:** real file-backed concurrent worker+HTTP requests (not only two connection reproduction), pause-before-start and resume exactly once across process restart, pause-during-import and pause-during-extraction liveness, crash recovery, MySQL semantics if supported, and permission testing. [Issue #36](https://github.com/luzay-max/DecisionAtlas/issues/36) blocks pause UI readiness. Keep both #28 and #35 Draft; no merges.

## Partial worker-start/queued-resume fix (2026-10-30)

The initial strict-xfail cases identified unsafe status transitions. A new candidate change protects `ImportJobRepository.mark_running` with a conditional `UPDATE status='queued'`, preventing repeated worker startup from resurrecting a terminal job or overwriting pause. `mark_resumed` now re-queues **not-yet-started** paused tasks, but resumes already-started tasks to `running`. `run_github_import` waits on a paused-before-start task while releasing its transaction between reads; a resumed queued task can then be claimed. The two strict-xfail cases have been promoted to ordinary passing tests and a new background-thread resume-once test was added.

**Still unresolved (#36):** During Artifact writes, the progress callback uses the same potentially uncommitted SQLite worker transaction; independent admin pause/resume may hit lock contention. Restart persistence, worker leases, crash recovery, and multiple-process durable queue semantics are NOT solved by this patch. Retain the positive SQLite contention test as a blocker and do not merge/enable pause UI on the strength of these worker-start tests alone.

## State-conditional pause/resume transitions (2026-10-30)

`mark_paused` and `mark_resumed` now use conditional UPDATE predicates so a stale admin SQLAlchemy session cannot overwrite a terminal job (pause only `queued/running`, resume only `paused`). The resume target is selected by a database-side `CASE` on `started_at IS NULL`, preserving queued-before-start semantics. New file-backed two-session regressions verify that stale pause after a concurrent success and stale resume after a concurrent failure are rejected, leaving the terminal state intact.

**Remaining risk:** SQLite can still block or fail an admin state transition while an uncommitted source writer holds a write lock. These guards prevent an invalid late write; they do not provide a second concurrently writable SQLite control plane, crash-safe worker leases, or a working cancel API. [Issue #36](https://github.com/luzay-max/DecisionAtlas/issues/36) remains open.

## Prefetch source Markdown before SQLite Artifact transaction (2026-10-30)

The source importer originally wrote issues/PRs/commits before launching and waiting on Markdown download futures. This held the SQLite Artifact writer lock across remote HTTP latency and delayed an admin pause/resume write even before the worker checked control state. The new candidate orders import steps as **fetch issue/PR/commit metadata + list tree + download/verify all selected Markdown → batch upsert Artifacts → commit once**. Existing checks for Git blob SHA and transactional all-or-nothing source capture remain in place.

New SQLite integration tests verify (1) an independent paused/resumed admin write can commit while a selected Markdown fetch is deliberately blocked, and Artifacts are not written until the document is released, and (2) a failed remote Markdown download leaves no partially inserted Artifact rows and permits an independent SQLite writer before failure. Previously covered normal import, idempotent retry, and moving-branch integrity tests remain required.

**Trade-off:** prefetching buffers all selected document contents until the write phase, increasing peak memory for repositories with many high-signal files. The current selector has no hard total-file/byte cap, so a follow-up must define bounded ingestion limits or spooling. This patch is **not** a solution for pause during an active SQLite Artifact write transaction, extraction-time candidate writes, crash-safe worker scheduling, or exact snapshot provenance. Keep [Issue #36](https://github.com/luzay-max/DecisionAtlas/issues/36) open, and do not enable UI pause/resume without the remaining controlled concurrency tests.
