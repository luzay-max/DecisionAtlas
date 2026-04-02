## Why

Imported drift reevaluation now classifies some previously noisy alerts more accurately, but older alert rows can remain in storage when an artifact changes from `possible_supersession` to `needs_review`. This leaves the UI showing two contradictory conclusions for the same artifact and accepted decision, which makes the improved classifier look broken.

## What Changes

- Replace stale drift alerts when reevaluation changes the semantic outcome for the same artifact and accepted decision.
- Ensure reevaluation removes obsolete stronger alerts instead of appending weaker replacements beside them.
- Preserve grouped weak follow-up behavior and stronger supersession alerts, but keep only the current result set after reevaluation.
- Clarify real imported drift behavior so reevaluation presents one current conclusion per artifact-decision thread.

## Capabilities

### New Capabilities
- `drift-alert-replacement`: Keep drift alerts in sync with the latest reevaluation outcome so stale alert types do not remain visible.

### Modified Capabilities
- `real-repository-outcomes`: Imported drift reevaluation should replace obsolete alert conclusions instead of surfacing both old and new results for the same artifact-decision thread.

## Impact

- `services/engine/app/drift/evaluator.py`
- `services/engine/app/repositories/drift_alerts.py`
- drift API and reevaluation tests
- drift UI validation for reevaluated imported workspaces
