## Why

Imported review quality is now stronger, but the imported why path is still too brittle after the first accepted baseline is established. Technically equivalent questions can still drift to weaker matches, good accepted decisions can remain stuck in `limited_support` or `evidence_limited`, and the product does not yet protect those regressions tightly enough across curated real repositories.

## What Changes

- Improve imported why-answer quality so accepted decisions are selected more consistently as the primary answer for focused questions.
- Strengthen citation assembly for imported why answers by using accepted-decision source refs and supporting chunk evidence more deliberately, without replacing the accepted decision as the trust anchor.
- Tighten the boundary between `ok`, `limited_support`, and `evidence_limited` so imported why responses fail closed when grounding is weak but upgrade more reliably when the accepted rationale thread is genuinely supported.
- Refine imported why next-action guidance so post-acceptance weak answers point users toward the right bounded follow-up instead of feeling ambiguous.
- Extend real-repo benchmark protection for imported why regressions and stronger post-acceptance expectations.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `why-answer-support-grading`: imported why answers should upgrade to `ok` or hold at `limited_support` based on stronger accepted-decision support rules, while weak matches remain explicitly bounded.
- `why-search-focus`: focused imported why questions should stay anchored to one primary accepted decision and admit supporting context more conservatively.
- `why-search-retrieval-quality`: retrieval-backed chunk evidence and technical-equivalent query handling should improve imported why support quality without weakening accepted-decision anchoring.
- `real-repository-outcomes`: imported why responses should expose clearer bounded follow-up guidance after an accepted baseline exists but the asked question is still weakly grounded.
- `lightweight-real-repo-benchmarks`: curated why benchmark fixtures should protect the stronger imported why outcomes and regression cases this slice targets.

## Impact

- Affected backend: `services/engine/app/retrieval/answering.py`, query rewrite / retrieval support, query API tests, retrieval tests, and benchmark validation.
- Affected frontend: imported why messaging and search-result tests where status interpretation or next-action guidance changes.
- Affected validation/docs: `examples/live-benchmarks/*.json`, benchmark fixture tests, and real-repo baseline documentation if protected outcomes change materially.
- Dependencies: no new external dependencies or database migration expected; reuse existing accepted decisions, source refs, artifact chunks, and workspace readiness structures.
