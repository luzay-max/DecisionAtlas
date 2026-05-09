## ADDED Requirements

### Requirement: Release evidence can be archived into readiness history
Generated release evidence bundles SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Release evidence is archived
- **WHEN** an operator archives readiness evidence with a release evidence JSON path
- **THEN** the history entry SHALL preserve the release evidence overall status, required gate statuses, advisory signal statuses, warnings, missing inputs, and source artifact filename.

#### Scenario: Release evidence is absent
- **WHEN** readiness history is archived without release evidence
- **THEN** the history entry SHALL record release evidence as not provided rather than passed.
