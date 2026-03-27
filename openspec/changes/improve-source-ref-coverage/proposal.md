## Why

Imported why-search now selects the right primary decision and can distinguish `limited_support` from true failure, but many accepted decisions still expose only one grounded citation. That keeps too many correct answers stuck in partial-support mode and hides the real bottleneck: thin source-ref coverage rather than poor why-answer focus.

## What Changes

- Improve source-ref coverage for extracted and accepted decisions so more decisions retain two or more grounded supporting references.
- Extend extraction and parsing flow to preserve multiple grounded quotes when the source artifact supports them.
- Make grounded-quote loss more explicit so operators can see when a decision was correct but citation coverage stayed thin.
- Validate imported why answers against live-style cases where one-citation answers should move toward fully supported outcomes after better grounding.

## Capabilities

### New Capabilities
- `source-ref-coverage`: Improves how extracted decisions retain multiple grounded source references from imported repository evidence.

### Modified Capabilities
- `why-answer-support-grading`: Increase the share of imported why answers that can satisfy the stronger `ok` support threshold by improving upstream source-ref coverage.
- `decision-extraction-conversion`: Improve post-extraction grounding so valid decisions are less likely to stop at a single usable citation.

## Impact

- Engine extraction and parsing flow
- Source-ref creation and grounding behavior
- Imported why-answer quality and support-state distribution
- Validation/benchmark fixtures for real repository analysis
