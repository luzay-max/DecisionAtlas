## 1. Retrieval Calibration

- [x] 1.1 Review current why-search query rewriting, significant-term extraction, hybrid retrieval weights, and primary accepted-decision selection.
- [x] 1.2 Add bounded technical alias normalization for recurring imported why vocabulary without introducing repository-specific hard-coded answers.
- [x] 1.3 Rebalance hybrid retrieval so semantic hits can rescue equivalent phrasing while lexical/source-ref fit still protects against neighboring-decision drift.
- [x] 1.4 Add engine retrieval tests for equivalent phrasing, synonym expansion, semantic rescue, and weaker lexical-neighbor avoidance.

## 2. Same-Thread Evidence Support

- [x] 2.1 Review existing artifact chunk support selection and identify where it can strengthen an already selected accepted decision.
- [x] 2.2 Tighten chunk support so it remains tied to the selected accepted decision or same rationale thread.
- [x] 2.3 Ensure chunk citations are de-duplicated against direct source refs and do not replace accepted-decision anchoring.
- [x] 2.4 Add API tests for direct-ref limited support, direct-ref plus same-thread chunk `ok`, and unrelated chunk evidence staying bounded.

## 3. Support State And Answer Context

- [x] 3.1 Audit current `ok`, `limited_support`, `evidence_limited`, and `review_required` transitions for imported workspaces.
- [x] 3.2 Keep high retrieval score from upgrading answers that lack accepted-decision fit or same-thread evidence.
- [x] 3.3 Add or update answer context fields only where needed to explain retrieval/support limitations.
- [x] 3.4 Add tests for accepted baseline without sufficient match staying `evidence_limited`.

## 4. Benchmark And Product Surface

- [x] 4.1 Add or update curated real-repo why benchmark cases for equivalent phrasing and expected primary rationale thread.
- [x] 4.2 Update benchmark/report output to record why-case observed status, citation count, expected term matches, and primary-thread match evidence where available.
- [x] 4.3 Update web copy/tests only if support-state wording or answer context changes.
- [x] 4.4 Update relevant project docs or plan notes if the implementation changes the current stage status or operator validation workflow.

## 5. Validation

- [x] 5.1 Run targeted engine API/retrieval tests for why-search behavior.
- [x] 5.2 Run benchmark fixture validation tests.
- [x] 5.3 Run web tests/typecheck if UI or API type surfaces changed.
- [x] 5.4 Run `openspec validate improve-imported-why-retrieval-quality --type change --strict`.
- [x] 5.5 Run broader validation if retrieval/support changes create release-risk behavior.
