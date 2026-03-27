## Why

Imported why-search now works against real accepted decisions, but it still over-merges adjacent decisions into one answer. That makes answers feel like stitched retrieval summaries instead of focused explanations, so the next highest-value improvement is to make why-search answer the user's specific question with a clearer primary decision and stricter merge behavior.

## What Changes

- Add a focused why-search capability that distinguishes a primary decision hit from optional supporting hits instead of concatenating nearby accepted decisions too freely.
- Strengthen query rewrite and question normalization so technically equivalent phrasings retrieve the same accepted decision more reliably.
- Tighten multi-hit merge rules so second-order hits only join the answer when they materially support the same rationale rather than merely sharing topical overlap.
- Update imported why-answer composition to produce a single focused answer with optional supporting context, while preserving citation-first trust boundaries.
- Add benchmark and regression coverage for "串题" cases where the current why path blends multiple adjacent decisions into one answer.

## Capabilities

### New Capabilities
- `why-search-focus`: governs focused decision selection, stricter multi-hit merge rules, and query normalization for why-search answers

### Modified Capabilities
- `real-repository-outcomes`: imported why-answer behavior will change so accepted-decision answers prefer a primary decision and only include supporting decisions when they truly reinforce the same rationale

## Impact

- Affected code:
  - `services/engine/app/retrieval/*`
  - `services/engine/app/api/query.py`
  - why-search result shaping in `apps/web`
- Affected APIs:
  - why-query response payloads and imported-workspace outcome wording
- Affected systems:
  - accepted-decision retrieval
  - imported why-answer quality benchmarks
