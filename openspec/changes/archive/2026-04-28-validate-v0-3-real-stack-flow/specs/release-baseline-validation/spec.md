## ADDED Requirements

### Requirement: Release baseline validation distinguishes confidence layers
The system SHALL distinguish mandatory canonical release validation from broader real-stack confidence validation so release gates remain deterministic while operator-recorded validation can still inform release readiness.

#### Scenario: Canonical release gate remains mandatory
- **WHEN** maintainers prepare a release or release-candidate baseline
- **THEN** the project SHALL continue to identify the canonical pre-release command as the mandatory local release gate

#### Scenario: Real-stack validation is recorded as a confidence layer
- **WHEN** maintainers perform broader v0.3 real-stack validation
- **THEN** release-facing docs or validation reports SHALL describe it as an operator-recorded confidence layer unless it has been made deterministic enough for default CI

#### Scenario: Release readiness references both layers clearly
- **WHEN** a release candidate is evaluated after real-stack validation
- **THEN** the project SHALL make clear which evidence came from the mandatory release gate and which evidence came from optional or operator-guided real-stack validation
