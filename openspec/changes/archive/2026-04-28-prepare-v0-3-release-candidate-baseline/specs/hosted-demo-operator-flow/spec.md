## ADDED Requirements

### Requirement: Hosted demo checks remain operator-guided for v0.3 RC
The system SHALL keep hosted demo health, smoke, reset, and reseed flows available for operator confidence while distinguishing them from the default v0.3 release-candidate gate.

#### Scenario: RC docs point to hosted checks as optional confidence
- **WHEN** v0.3 release-candidate docs mention hosted demo validation
- **THEN** they SHALL describe hosted health and smoke checks as operator-guided confidence checks rather than as replacements for canonical pre-release validation

#### Scenario: Hosted preview remains a follow-up phase
- **WHEN** v0.3 RC readiness is described
- **THEN** the project SHALL state that externally hosted preview preparation is a later phase after the release-candidate baseline is frozen

#### Scenario: Hosted operator paths use current scripts
- **WHEN** hosted demo docs describe local operator rehearsal
- **THEN** they SHALL reference the currently supported stack, health, smoke, reset, and reseed commands rather than removed development scripts
