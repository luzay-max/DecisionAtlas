## ADDED Requirements

### Requirement: Benchmark comparison can be archived into readiness history
Real-repo benchmark comparison reports SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Benchmark comparison is archived
- **WHEN** an operator archives readiness evidence with a benchmark comparison JSON path
- **THEN** the history entry SHALL preserve repository count, movement counts, regression count, improvement count, operational blocker count, and source artifact filename.

#### Scenario: Benchmark comparison is absent
- **WHEN** readiness history is archived without benchmark comparison evidence
- **THEN** the history entry SHALL record benchmark comparison as not provided rather than passed.
