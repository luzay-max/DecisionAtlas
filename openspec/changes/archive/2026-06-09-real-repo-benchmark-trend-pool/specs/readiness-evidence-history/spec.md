## ADDED Requirements

### Requirement: Readiness materials can reference benchmark trend evidence
Readiness evidence workflows SHALL allow operators to attach benchmark trend evidence alongside release evidence, hosted readiness, and benchmark comparison evidence.

#### Scenario: Trend evidence exists for a release rehearsal
- **WHEN** benchmark trend evidence is generated for a release rehearsal
- **THEN** readiness-facing Markdown or handoff summaries MUST expose the trend status and recommended follow-up without replacing the benchmark comparison artifact

#### Scenario: Trend evidence is missing
- **WHEN** benchmark trend evidence is not supplied
- **THEN** readiness-facing summaries MUST keep the missing trend evidence visible as `not_provided` or `warning` rather than silently dropping it
