## Why

DecisionAtlas v0.3 RC can establish accepted imported baselines, but why-search still risks missing the right decision when users ask with equivalent technical wording or when direct source refs are only partially sufficient. This change improves imported why-search retrieval quality while preserving the conservative trust boundary: accepted decisions remain the answer anchor, and weak evidence still fails closed.

## What Changes

- Improve imported why-search normalization for common technical synonyms and aliases so equivalent questions can retrieve the same primary accepted decision.
- Rebalance hybrid retrieval so semantic similarity can materially help recall without letting unrelated lexical neighbors dominate.
- Use artifact chunks as a supporting evidence layer for an already selected accepted decision, not as a replacement answer source.
- Make support outcomes more explicit across `ok`, `limited_support`, `evidence_limited`, and `review_required`.
- Add benchmark and targeted tests for equivalent imported questions, same-thread chunk support, weak-match failure, and neighboring-decision separation.
- Update operator-facing quality/reporting expectations so why-search retrieval quality is visible in real-repository validation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `why-search-retrieval-quality`: strengthen equivalent-question retrieval, semantic contribution, and accepted-decision anchoring.
- `why-answer-support-grading`: clarify how direct source refs and same-thread chunk evidence affect `ok`, `limited_support`, `evidence_limited`, and `review_required`.
- `real-repository-outcomes`: extend real-repository validation expectations to record imported why-search retrieval usefulness after a first accepted baseline exists.

## Impact

- Engine why-search and retrieval logic:
  - query normalization / synonym handling
  - hybrid scoring and ranking
  - accepted-decision selection
  - artifact chunk support selection
- API response support state and answer context where needed.
- Benchmark fixtures and live real-repository validation reporting.
- Web why-search copy only if response guidance needs clearer support-state wording.
- Tests:
  - engine why-search retrieval tests
  - support grading tests
  - benchmark fixture validation tests
  - focused web tests if support-state copy changes
