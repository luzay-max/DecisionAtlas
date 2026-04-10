# 2026-04-09 Update Log

## Summary

Today's work focused on tightening the imported-workspace product loop so it feels closer to a release-quality system instead of a collection of separate quality experiments.

The main outcomes are:

- imported why-search retrieval is stronger and can now use chunk-backed evidence to upgrade some answers to `ok`
- imported workspace readiness is now surfaced more clearly across dashboard and search
- indexing is now structure-aware, with chunk metadata preserved and used in why-support ranking
- release-facing docs now better match the current shipped capability set

## Completed

### Imported why-search retrieval quality

- Strengthened query rewrite for technical aliases and equivalent repository phrasing.
- Rebalanced hybrid retrieval so vector evidence can break near-ties instead of acting like negligible noise.
- Added chunk-backed supporting evidence behind the accepted-decision anchor.
- Confirmed the imported `browser-use` why case for HTTP downloads now resolves to `ok` with stronger supporting citations.

### Imported workspace readiness surface

- Expanded imported readiness to include:
  - review readiness
  - why readiness
  - drift readiness
  - recommended next actions
- Updated dashboard and search to reuse the same imported readiness semantics instead of inferring their own next steps.
- Improved product copy so imported workspaces explain what the operator should do next.

### Indexing modernization for real evidence

- Replaced flat paragraph-only chunking with structure-aware chunking.
- Added bounded overlap for oversized sections.
- Persisted chunk metadata such as:
  - `heading_path`
  - `section_title`
  - `chunk_role`
  - `boundary_kind`
- Updated why supporting-evidence ranking so structured section chunks are preferred over weaker flat chunks when supporting the same accepted decision.
- Applied the new artifact-chunk metadata migration locally and validated the imported `browser-use` why flow after reindexing.

### Release-quality cleanup

- Updated `README.md` to reflect the current imported-workspace baseline and current priorities.
- Updated `quick-start.md` with real-repo smoke guidance and clearer bounded-outcome explanations.
- Updated `demo-script.md` to include an optional short imported-repo credibility proof.
- Updated `release-checklist.md` to include imported readiness and structured-evidence checks.
- Updated the roadmap so it reflects the shipped why, readiness, and indexing work.
- Added local noise patterns such as `.codex/`, `erroImg/`, and `1.txt` to `.gitignore`.
- Finished the remaining release-facing docs:
  - `faq.md`
  - `release-notes-v0.2.md`
  - `real-repository-validation-baseline.md`
- Added `github_open_source_project_research_report_zh_final.docx` to `.gitignore` so it stays out of product commits.

### Release blocker fixes

- Updated engine tests to match the current parser contract and drift behavior:
  - `services/engine/tests/extractor/test_parser.py`
  - `services/engine/tests/db/test_schema.py`
  - `services/engine/tests/drift/test_evaluator.py`
  - `services/engine/tests/api/test_drift_api.py`
- Stabilized semantic-drift test fixtures with explicit semantic-recall patching so evaluator tests do not drift with retrieval heuristics.
- Fixed the Playwright demo smoke flow:
  - avoided the duplicated import-success text strict-mode locator
  - aligned the drift assertion with the current UI label (`possible drift`)

### Lightweight real-repo benchmark capture (2026-04-10 follow-up)

- Created and implemented `capture-lightweight-real-repo-benchmarks`.
- Added fixture-backed real-repo checks:
  - `examples/live-benchmarks/why-cases.json`
  - `examples/live-benchmarks/drift-cases.json`
- Added `browser-use/browser-use` to the live benchmark repository set.
- Extended `scripts/ci/run_benchmark.py` so default validation checks repository, why-case, and drift-case fixture shape offline.
- Added optional `--live-real-repos` mode for focused why checks against an already-running local API and existing imported workspaces.
- Updated `real-repository-validation-baseline.md` to point to the fixture-backed benchmark cases.
- Archived the OpenSpec change and synced:
  - `lightweight-real-repo-benchmarks`
  - `real-repository-outcomes`

### OpenSpec

- Completed and archived:
  - `improve-why-search-retrieval-quality`
  - `improve-imported-workspace-readiness-surface`
  - `modernize-indexing-for-real-evidence`
  - `capture-lightweight-real-repo-benchmarks`

## Validation

- `.\.venv\Scripts\python -m pytest tests\indexing\test_chunker.py tests\indexing\test_index_artifact.py tests\retrieval\test_answering.py tests\api\test_query_api.py -q` in `services/engine`
- `pnpm --filter @decisionatlas/web test -- search-page`
- `pnpm --filter @decisionatlas/web typecheck`
- `.\.venv\Scripts\python -m pytest -q` in `services/engine` -> `132 passed`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` -> passed
- `pnpm --filter @decisionatlas/web exec playwright test apps/web/tests-e2e/demo-smoke.spec.ts` -> passed
- `python scripts\ci\run_benchmark.py` -> passed with repository, why-case, and drift-case fixture validation
- `.\.venv\Scripts\python -m pytest tests\evals\test_benchmark_fixtures.py -q` -> `4 passed`
- `python scripts\ci\run_benchmark.py --live-real-repos` -> passed against the local `github-browser-use-browser-use` workspace
- real imported workspace validation against `github-browser-use-browser-use` for:
  - imported why-search retrieval quality
  - imported readiness surface
  - structure-aware chunk-backed evidence

## Git / Branching

- Recorded the day in a dedicated update log commit: `03bd370` `docs: add 2026-04-09 update log`
- Finished the release cleanup tail as `be1945b` `docs: finish release quality cleanup`
- Landed the release blocker fixes as `ed92875` `test: fix release smoke and engine regressions`
- Pushed the branch updates to `origin/feat/expand-real-repo-ingest`
- Fast-forward merged the branch into `main` and pushed `origin/main`
- Switched back to `feat/expand-real-repo-ingest` after the merge to keep working there

## Current Reading of the Product

- The real imported-repo lane is now materially stronger than it was at the start of the drift-quality work.
- Why-search, drift semantics, readiness surface, and indexing all now fit together more coherently.
- The release-quality cleanup pass is now largely complete, including smoke coverage and pre-release verification.
- The highest-value remaining work is no longer “make the imported lane basically work,” but “keep the current system legible and protect it from regressions.”

## Next Suggested Direction

- Decide whether the two remaining local-only documents should be committed or intentionally left out of the repo.
- After that, move on to heavier v0.3 platform capabilities, starting with platform-boundary design before GitHub App implementation.
