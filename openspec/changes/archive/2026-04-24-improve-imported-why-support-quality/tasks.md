## 1. Engine imported why support quality

- [x] 1.1 Tighten primary accepted-decision selection for focused imported why questions so weaker neighboring hits do not win by accident.
- [x] 1.2 Refine imported support grading to evaluate grounded source refs plus same-thread chunk support, allowing stronger `ok` upgrades while keeping weak post-acceptance matches `evidence_limited`.
- [x] 1.3 Keep supporting context conservative for focused imported questions while preserving broad-question support behavior where it still qualifies.
- [x] 1.4 Add or update engine retrieval tests for equivalent phrasing, chunk-backed support upgrades, and weak accepted-baseline mismatch fallbacks.

## 2. API and product-facing why behavior

- [x] 2.1 Update why-query API tests to protect the refined imported statuses, primary decision anchoring, and bounded next-action guidance.
- [x] 2.2 Update web why-search handling if imported status wording, supporting-context visibility, or next-action rendering changes.
- [x] 2.3 Add or update frontend search-page tests covering stronger imported `ok` / `limited_support` behavior and focused-answer stability.

## 3. Benchmarks and validation

- [x] 3.1 Extend curated why benchmark fixtures with post-acceptance support-quality expectations and at least one equivalent-question regression case.
- [x] 3.2 Update benchmark fixture tests and real-repo baseline docs if the protected imported why expectations change materially.
- [x] 3.3 Run targeted engine why tests and offline benchmark validation.
- [x] 3.4 Run the canonical pre-release validation gate before considering the slice complete.
