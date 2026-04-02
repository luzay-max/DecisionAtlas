## 1. Supersession Boundary Logic

- [x] 1.1 Identify the semantic cases where replacement language currently over-promotes implementation substitutions into `possible_supersession`.
- [x] 1.2 Tighten classifier logic so decision-layer replacement evidence is required before emitting `possible_supersession`.
- [x] 1.3 Preserve `needs_review` fallback for related implementation substitutions that remain reviewable.

## 2. Drift Semantics

- [x] 2.1 Update drift summaries or confidence semantics so implementation substitutions read as weaker review guidance.
- [x] 2.2 Keep grouped follow-up behavior intact while refining only the supersession boundary.
- [x] 2.3 Keep manual drift evaluation flow unchanged.

## 3. Validation

- [x] 3.1 Add engine regression coverage for implementation-level replacements that should no longer over-trigger supersession.
- [x] 3.2 Add API/web regression coverage for the refined supersession semantics.
- [x] 3.3 Validate the change against the previously noisy imported browser-use drift cases before closing the change.
