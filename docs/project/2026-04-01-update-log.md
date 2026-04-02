# 2026-04-01 Update Log

## Summary

Today’s work focused on reducing imported drift noise after the earlier drift-precision change had already made `possible_supersession` more conservative.

The main outcome is that repeated weak follow-up alerts tied to the same accepted decision are now collapsed into a more compact review thread instead of rendering as many nearly identical `needs_review` cards.

## Completed

### Drift follow-up noise reduction

- Added grouping logic in the drift evaluator for repeated weak `needs_review` alerts that point to the same accepted decision.
- Preserved stronger `possible_supersession` alerts as independent signals.
- Updated grouped follow-up summaries so they read as one review thread, not many separate warnings.
- Updated the drift web UI to show an explicit grouped-follow-up hint when several implementation follow-ups are condensed.

### Regression coverage

- Added engine tests for:
  - repeated follow-up artifacts collapsing into one grouped alert
  - grouped weak alerts coexisting with independent `possible_supersession`
- Added API regression coverage for grouped follow-up summaries.
- Added web regression coverage for grouped drift alert rendering.

### OpenSpec

- Completed and archived:
  - `improve-drift-precision`
  - `reduce-drift-followup-noise`

## Validation

- `.\.venv\Scripts\python -m pytest tests\drift\test_evaluator.py tests\api\test_drift_api.py -q` in `services/engine`
- `pnpm --filter @decisionatlas/web test -- drift-detail drift-page`
- `pnpm --filter @decisionatlas/web typecheck`

## Current Reading of the Product

- Drift is now meaningfully better than before:
  - broad-doc false positives are lower
  - repeated weak follow-up alerts are more compact
- The remaining main drift issue is narrower:
  - some `possible_supersession` alerts still appear too aggressive for implementation-level replacement work

## Next Suggested Direction

- Tighten `possible_supersession` further so implementation-level substitutions are less likely to be interpreted as decision-level replacement.
