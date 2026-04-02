## 1. Semantic Classifier Precision

- [x] 1.1 Tighten `possible_supersession` classification so it requires stronger replacement evidence than the current score-plus-marker rule.
- [x] 1.2 Add artifact-family-aware suppression or downgrade logic for broad docs such as changelogs, contributing material, roadmap notes, and implementation-phase docs.
- [x] 1.3 Preserve `needs_review` as the default fallback when overlap is meaningful but replacement evidence is still weak.

## 2. Alert Semantics

- [x] 2.1 Update semantic drift summaries so `possible_supersession` reads as cautious review guidance rather than an implied confirmed replacement.
- [x] 2.2 Update drift confidence and wording in the web UI so stronger and weaker semantic alerts are easier to distinguish.
- [x] 2.3 Keep the existing manual drift evaluation flow and imported drift-state behavior unchanged while improving only alert precision and semantics.

## 3. Validation

- [x] 3.1 Add engine tests covering broad-document false positives, stronger supersession evidence, and `needs_review` fallback behavior.
- [x] 3.2 Add API/web regression coverage for the updated drift summaries and alert presentation.
- [x] 3.3 Validate the change against at least one previously noisy imported-repo drift case before closing the change.
