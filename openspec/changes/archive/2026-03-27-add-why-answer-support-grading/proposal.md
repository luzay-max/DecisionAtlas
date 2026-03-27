## Why

Imported why-search now selects the right primary decision more reliably, but it still collapses partially grounded answers into `insufficient_evidence` when only one strong citation is available. That makes the product understate what it knows and hides the difference between "wrong or missing answer" and "correct answer with limited support."

## What Changes

- Add a graded imported why-answer outcome for cases where the primary accepted decision is correct but supporting citations are still thin.
- Distinguish `limited_support` from `insufficient_evidence` and preserve the current conservative fail-closed path for truly weak or missing grounding.
- Update imported why UI and readiness messaging so users can tell when an answer is directionally correct but not yet fully backed.
- Add regression coverage for focused why-answers that currently return one citation and are therefore mislabeled as evidence failures.

## Capabilities

### New Capabilities
- `why-answer-support-grading`: Grades imported why-answers by support strength so partially grounded answers can be surfaced without pretending they are fully supported.

### Modified Capabilities
- `real-repository-outcomes`: Imported why-answer outcomes and next-step guidance need to distinguish limited support from true evidence failure.
- `why-search-focus`: Focused why-answer composition needs to carry support-strength state alongside the primary decision and optional supporting context.

## Impact

- Engine why-answer selection and response payloads.
- Imported workspace why-result rendering and state messaging in the web app.
- API and regression tests for imported why-answer status handling.
- OpenSpec requirements for imported why behavior and why-search result semantics.
