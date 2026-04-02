## Why

Imported drift evaluation is now more conservative about `possible_supersession`, but it still emits too many weak `needs_review` alerts for implementation follow-up work around the same accepted decision. This makes drift harder to scan because users see many closely related reminders that do not actually represent a decision change.

## What Changes

- Reduce drift noise from implementation-follow-up artifacts that continue the same accepted decision rather than changing it.
- Group or suppress repeated `needs_review` alerts that point at the same accepted decision and rationale thread.
- Keep stronger replacement signals intact while making weaker follow-up alerts more compact and easier to interpret.
- Clarify imported drift UI semantics so grouped follow-up work reads as one review thread instead of many separate warnings.

## Capabilities

### New Capabilities
- `drift-followup-noise`: Reduce repeated drift alerts caused by implementation follow-ups around the same accepted decision.

### Modified Capabilities
- `real-repository-outcomes`: Imported drift results should present weaker follow-up material in a more compact, less repetitive form.

## Impact

- `services/engine/app/drift/*`
- drift evaluator and alert shaping logic
- drift API response shape or alert summary fields
- `apps/web/components/drift/*`
- imported drift regression coverage for noisy real-repo cases
