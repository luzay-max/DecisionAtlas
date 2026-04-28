## ADDED Requirements

### Requirement: v0.3 validation records hosted preview readiness separately
The system SHALL record hosted preview readiness as a distinct validation layer after the v0.3 RC baseline and real-stack validation work.

#### Scenario: Hosted preview report references RC baseline
- **WHEN** a hosted preview readiness report is created
- **THEN** it SHALL identify the RC baseline or current commit being evaluated and distinguish it from earlier local validation evidence

#### Scenario: Hosted checks record environment availability
- **WHEN** hosted health, smoke, reset, or reseed checks cannot be run against an external environment
- **THEN** the report SHALL mark them as operator-guided or unavailable rather than silently treating them as passed

#### Scenario: Hosted preview blockers are explicit
- **WHEN** hosted preview validation finds a blocking issue
- **THEN** the report SHALL identify the impacted lane, observed result, and required follow-up before external demonstration
