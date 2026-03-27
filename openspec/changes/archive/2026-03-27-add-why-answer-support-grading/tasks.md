## 1. Why Support Classification

- [x] 1.1 Add backend why-answer classification for `limited_support` alongside existing `ok`, `review_required`, and `insufficient_evidence` outcomes.
- [x] 1.2 Keep the current primary-decision-first why flow while grading support strength after primary decision selection.
- [x] 1.3 Preserve the existing fail-closed behavior for cases with no accepted grounding or no grounded citations.

## 2. API and UI Semantics

- [x] 2.1 Extend the why-search response contract so clients can read the new support-grading state directly.
- [x] 2.2 Update imported why-search UI copy and status rendering to distinguish `limited_support` from full success and from insufficient evidence.
- [x] 2.3 Ensure next-step guidance for partially supported why answers remains conservative and actionable.

## 3. Validation

- [x] 3.1 Add engine and API tests for one-citation imported why answers that should now return `limited_support`.
- [x] 3.2 Add frontend tests for rendering partially supported why answers without mislabeling them as failures.
- [x] 3.3 Re-run focused imported why benchmark questions to verify that correct-but-thinly-supported answers are no longer collapsed into `insufficient_evidence`.
