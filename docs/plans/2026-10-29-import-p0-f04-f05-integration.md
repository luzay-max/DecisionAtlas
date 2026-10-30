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
