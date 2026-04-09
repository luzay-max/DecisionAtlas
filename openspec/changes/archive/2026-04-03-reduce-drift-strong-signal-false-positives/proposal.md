## Why

Imported drift now avoids stale alerts and most weak follow-up noise, but some implementation-heavy bugfixes and lifecycle fixes still surface as `possible_supersession`. This keeps the drift surface more alarming than it should be and makes stronger signals less trustworthy in real repositories.

## What Changes

- Further reduce false positives in stronger drift signals so implementation-level fixes are less likely to land in `possible_supersession`.
- Require tighter evidence that the newer artifact is replacing the accepted decision itself rather than repairing or extending the same chosen path.
- Preserve weaker review visibility through `needs_review` when artifacts remain relevant but do not justify stronger replacement semantics.
- Clarify spec-level drift behavior so imported workspaces reserve stronger alerts for clearer decision-change signals.

## Capabilities

### New Capabilities
- `drift-strong-signal-false-positives`: Reduce false positives in stronger drift alerts when later artifacts mostly reflect bugfixes, lifecycle fixes, or supporting implementation work.

### Modified Capabilities
- `drift-precision`: Tighten the stronger-signal bar so implementation-heavy fixes do not over-trigger `possible_supersession`.
- `drift-supersession-boundary`: Refine the decision-layer replacement boundary for real noisy imported-repo cases.
- `real-repository-outcomes`: Imported drift results should keep implementation-heavy fixes on the weaker review path unless stronger decision replacement evidence is present.

## Impact

- `services/engine/app/drift/semantic_classifier.py`
- semantic drift evaluator/classifier tests
- drift API and imported drift UI semantics
- real imported-repo validation cases, especially browser-use style drift examples
