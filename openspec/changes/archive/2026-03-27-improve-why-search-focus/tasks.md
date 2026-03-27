## 1. Query Rewrite

- [x] 1.1 Expand why-query normalization beyond lowercase and whitespace collapsing
- [x] 1.2 Add a small technical synonym and alias layer for imported why-questions
- [x] 1.3 Add tests that equivalent phrasings still retrieve the same primary accepted decision

## 2. Primary Decision Selection

- [x] 2.1 Refactor why-search hit selection so it chooses one primary accepted decision before considering any secondary support
- [x] 2.2 Add stricter support-eligibility rules for secondary hits so nearby but distinct decisions do not automatically merge into the same answer
- [x] 2.3 Add regression coverage for imported-workspace cases where current why-search over-blends adjacent decisions

## 3. Focused Answer Composition

- [x] 3.1 Update answer shaping so the main why-answer is anchored on the primary accepted decision
- [x] 3.2 Present optional supporting context separately from the main answer body when a secondary decision is truly needed
- [x] 3.3 Preserve citation-first trust behavior and existing evidence-limited / review-required outcomes

## 4. Validation

- [x] 4.1 Add engine and API tests for single-decision focus and support-hit exclusion
- [x] 4.2 Add web tests for focused why-answer rendering when support context is present
- [x] 4.3 Re-run imported-workspace benchmark questions to compare focus quality before and after the change
