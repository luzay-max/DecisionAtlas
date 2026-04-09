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

### OpenSpec

- Completed and archived:
  - `improve-why-search-retrieval-quality`
  - `improve-imported-workspace-readiness-surface`
  - `modernize-indexing-for-real-evidence`

## Validation

- `.\.venv\Scripts\python -m pytest tests\indexing\test_chunker.py tests\indexing\test_index_artifact.py tests\retrieval\test_answering.py tests\api\test_query_api.py -q` in `services/engine`
- `pnpm --filter @decisionatlas/web test -- search-page`
- `pnpm --filter @decisionatlas/web typecheck`
- real imported workspace validation against `github-browser-use-browser-use` for:
  - imported why-search retrieval quality
  - imported readiness surface
  - structure-aware chunk-backed evidence

## Current Reading of the Product

- The real imported-repo lane is now materially stronger than it was at the start of the drift-quality work.
- Why-search, drift semantics, readiness surface, and indexing all now fit together more coherently.
- The highest-value remaining work is no longer “make the imported lane basically work,” but “package and validate the current system like a release.”

## Next Suggested Direction

- Finish the release-quality cleanup pass.
- Keep benchmark capture lightweight and tied to real-repo smoke cases instead of turning it into a large separate platform effort.
- Only after that, move on to heavier v0.3 platform capabilities.
