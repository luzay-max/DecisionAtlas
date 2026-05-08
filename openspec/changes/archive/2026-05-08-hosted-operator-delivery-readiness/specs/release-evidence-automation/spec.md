## ADDED Requirements

### Requirement: Release evidence can be referenced by hosted readiness
Generated release evidence bundles SHALL be usable as referenced input for hosted/operator readiness records without changing release gate semantics.

#### Scenario: Hosted readiness consumes release evidence reference
- **WHEN** a hosted readiness record includes a release evidence bundle
- **THEN** the hosted readiness record SHALL show the release evidence status and source path
- **AND** it SHALL keep hosted readiness classification separate from canonical release validation.

#### Scenario: Release evidence warning remains disclosed
- **WHEN** a referenced release evidence bundle reports warning, caution, missing input, or advisory blockers
- **THEN** hosted readiness output SHALL disclose that status rather than treating the bundle as clean pass.
