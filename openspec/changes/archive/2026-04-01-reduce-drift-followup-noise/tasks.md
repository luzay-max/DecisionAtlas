## 1. Drift Grouping Logic

- [x] 1.1 Identify repeated weak drift alerts that target the same accepted decision and chosen-option thread.
- [x] 1.2 Add evaluator logic to collapse or suppress repeated implementation-follow-up `needs_review` alerts while preserving one representative review signal.
- [x] 1.3 Preserve independent `possible_supersession` alerts when stronger replacement evidence exists.

## 2. Alert Semantics and Presentation

- [x] 2.1 Update drift alert summaries or API shaping so grouped follow-up work reads like one review thread instead of repeated warnings.
- [x] 2.2 Update the web drift surface to render grouped or deduplicated follow-up alerts clearly.
- [x] 2.3 Keep manual drift evaluation flow unchanged while reducing repeated weak-alert volume.

## 3. Validation

- [x] 3.1 Add engine regression coverage for repeated follow-up artifacts on the same accepted decision.
- [x] 3.2 Add API/web regression coverage for compact grouped follow-up presentation.
- [x] 3.3 Validate the change against the previously noisy imported browser-use drift case before closing the change.
