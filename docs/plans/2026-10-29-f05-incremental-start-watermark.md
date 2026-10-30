# F05 — Conservative incremental sync start boundary (interim fix)

**Date:** 2026-10-29  
**Base:** `main@8aa461f5bc30f16e023c9c00f0d641794fd16f86`  
**Status:** Draft PR; do not merge automatically.

## Narrow scope
- Previously `since_last_sync` took the **previous successful job's finished_at** as the next GitHub source lower bound. Updates during issue/PR/commit listing → indexing/LLM extraction could be skipped forever.
- Anchor from **previous successful job's started_at** (fallback `created_at` for preexisting/legacy records); subtract fixed **5-minute overlap** to handle edge timestamps and ordinary clock skew.
- Normalize naive/aware UTC timestamps from SQLite and DB before generating GitHub API `since`.
- Record effective `summary.sync_window` (source_since, basis, overlap_seconds) before source import so failed jobs are diagnosable, and only successful jobs become the next anchor via existing `latest_success_for_repo` query.

## Regression tests
- [ ] Previous started 10:00, finished 10:15, changed source 10:03: next since is 09:55 and includes the update.
- [ ] Legacy success without started_at uses created_at rather than finished_at.
- [ ] Failed incremental jobs do not replace the last successful anchor; retry uses the same since.
- [ ] Full GitHub Actions Windows CI passes on final PR head.

## Important limitations
This is a **bounded mitigation, not complete F05 cursor semantics**. GitHub API Issues and commits accept `since`, while PRs still page updated-desc and filter locally (so large result limits need F04). Commits can be rebased/force-pushed, source timestamps may be late or malformed, and five minutes does not guarantee arbitrary clock skew or provider eventual consistency. Full correctness requires per-stream cursor/overlap and immutable source revisions (F06); rejected/partial coverage must not silently advance watermark (F04). This change does not address candidate re-extraction on changed Artifacts, and does not promise true continuous-sync semantics.

No migrations, new providers, live GitHub API calls, paid LLM, or changes/merges to Draft PRs #26/#28/#29/#30. Production integration acceptance remains separate.
