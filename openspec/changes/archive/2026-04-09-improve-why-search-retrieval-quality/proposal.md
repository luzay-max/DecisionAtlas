## Why

Imported why-search is now trustworthy enough to use, but retrieval quality is still the main bottleneck. Slight wording mismatches, low vector influence, and thin artifact-evidence support keep too many valid imported why-questions in weaker states even when the workspace already contains the right rationale.

## What Changes

- Improve `rewrite_query()` so technically equivalent why-questions normalize toward the same accepted decision.
- Rebalance hybrid retrieval so vector similarity contributes meaningfully instead of acting as a near-no-op.
- Add artifact-chunk evidence retrieval as a support layer behind accepted decisions to improve explanation quality and citation density.
- Keep accepted decisions as the trust anchor and avoid replacing the why path with freeform answer generation.
- Add regression and benchmark coverage around real imported why questions.

## Capabilities

### New Capabilities
- `why-search-retrieval-quality`: Retrieval-side improvements for imported why-search, including stronger query normalization, hybrid weighting, and chunk-backed evidence support.

### Modified Capabilities
- `why-search-focus`: Focused why answers now need stronger retrieval behavior so the right primary decision remains stable across wording variation.
- `why-answer-support-grading`: Support grades need to reflect improved retrieval and evidence assembly without weakening the meaning of `ok` or `limited_support`.
- `real-repository-outcomes`: Imported why outcomes need to expose improved retrieval-backed evidence behavior while preserving decision-grounded trust.

## Impact

- Affected engine retrieval modules: query rewrite, hybrid search, vector/full-text combination, and why answer assembly.
- Affected artifact index usage because chunk retrieval becomes a direct support layer for imported why answers.
- Affected tests and benchmark fixtures for imported repository why questions.
