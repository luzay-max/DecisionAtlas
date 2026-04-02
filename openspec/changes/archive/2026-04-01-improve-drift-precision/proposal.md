## Why

Imported drift evaluation now works end to end, but many alerts still feel too broad to trust. In real repositories, `possible_supersession` can over-trigger on changelogs, contributing docs, and other follow-up artifacts that are related to a decision without actually meaning the decision was replaced.

## What Changes

- Tighten semantic drift classification so `possible_supersession` requires stronger replacement signals than broad topical overlap.
- Reduce false positives from broad artifact families such as changelogs, contributing docs, roadmap notes, and implementation-planning material.
- Improve drift alert wording and confidence semantics so alerts read like review signals rather than implied conclusions.
- Preserve the current manual evaluation flow and accepted-decision trust boundary while making resulting alerts more credible.

## Capabilities

### New Capabilities
- `drift-precision`: Covers stricter semantic drift classification, broad-document suppression, and clearer drift alert semantics.

### Modified Capabilities
- `real-repository-outcomes`: Imported drift outcomes need more precise alert semantics so users can distinguish credible supersession signals from broad follow-up material that only warrants review.

## Impact

- Engine semantic drift classifier and evaluator
- Drift alert summaries and confidence labels returned by the API
- Drift UI wording and regression tests
- Imported-workspace drift usability and overall trust in live repository results
