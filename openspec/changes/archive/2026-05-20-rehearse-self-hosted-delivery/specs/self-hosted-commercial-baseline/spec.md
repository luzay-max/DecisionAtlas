## ADDED Requirements

### Requirement: Self-hosted customer handoff references rehearsal evidence
The system SHALL require self-hosted customer handoff claims to reference completed rehearsal evidence or disclose why rehearsal evidence is missing.

#### Scenario: Handoff claims readiness
- **WHEN** documentation, release notes, or customer handoff material claims that a self-hosted deployment is ready for evaluation or pilot use
- **THEN** the material SHALL reference a completed self-hosted delivery rehearsal, readiness evidence history entry, or equivalent evidence package
- **AND** it SHALL disclose any warning, blocking, operator-guided, known-limitation, or not-provided states.

#### Scenario: Rehearsal evidence is missing
- **WHEN** a handoff is prepared without completed rehearsal evidence
- **THEN** the handoff SHALL state that rehearsal evidence is missing
- **AND** it SHALL avoid claiming clean self-hosted readiness.
