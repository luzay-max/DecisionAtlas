## Why

Drift follow-up noise is now lower, but some implementation-level substitutions still surface as `possible_supersession` even when they look more like a change in execution path, dependency choice, or supporting mechanism than a true replacement of the accepted decision. This keeps drift more alarming than it should be for real imported repositories.

## What Changes

- Tighten the semantic boundary for `possible_supersession` so implementation-level substitutions are less likely to be treated as decision-level replacement.
- Require stronger evidence that a later artifact is replacing the accepted decision itself rather than merely changing the implementation underneath it.
- Keep weaker but still relevant signals available through `needs_review` instead of over-promoting them.
- Clarify drift wording so `possible_supersession` remains reserved for higher-confidence decision replacement signals.

## Capabilities

### New Capabilities
- `drift-supersession-boundary`: Distinguish decision replacement from implementation substitution during semantic drift classification.

### Modified Capabilities
- `drift-precision`: Tighten the supersession evidence bar so implementation-level substitutions do not over-trigger replacement alerts.
- `real-repository-outcomes`: Imported drift results should preserve stronger replacement semantics only for real decision-change signals.

## Impact

- `services/engine/app/drift/semantic_classifier.py`
- semantic drift evaluator and classifier tests
- drift API summaries and confidence semantics
- drift UI wording for imported workspaces
- real imported-repo drift validation cases
