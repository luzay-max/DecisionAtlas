## 1. Strong-Signal Heuristics

- [x] 1.1 Identify the remaining noisy `possible_supersession` patterns in imported drift, especially bugfix, lifecycle, and support-path maintenance artifacts.
- [x] 1.2 Tighten classifier logic so implementation-heavy fixes need stronger decision-displacement evidence before reaching `possible_supersession`.
- [x] 1.3 Preserve weaker `needs_review` fallback for artifacts that remain relevant but do not justify stronger replacement semantics.

## 2. Drift Semantics

- [x] 2.1 Keep grouped follow-up and stale-alert replacement behavior intact while refining only stronger-signal false positives.
- [x] 2.2 Keep imported drift semantics aligned so implementation-heavy maintenance stays on the weaker review path.
- [x] 2.3 Keep manual drift evaluation flow unchanged.

## 3. Validation

- [x] 3.1 Add engine regression coverage for browser-use style bugfix and lifecycle-repair cases that should no longer over-trigger `possible_supersession`.
- [x] 3.2 Add API/web regression coverage if alert summaries or confidence semantics shift for those cases.
- [x] 3.3 Validate the updated classifier against the current imported drift output before closing the change.
