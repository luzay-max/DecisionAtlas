# hosted-demo-operator-flow Specification

## Purpose
Define the operator-facing contract for running, checking, recovering, and presenting a single-machine hosted DecisionAtlas demo while keeping the stable seeded demo lane separate from imported real-repository workspaces.
## Requirements
### Requirement: Hosted demo defines an operator-facing environment contract
The system SHALL define a hosted-demo environment contract that identifies the required services, required environment variables, optional live-provider extensions, and backend-only secret boundaries for the single-machine demo deployment.

#### Scenario: Hosted demo environment identifies required services and variables
- **WHEN** an operator prepares a hosted demo environment
- **THEN** the project SHALL document the required service topology and the minimum environment variables needed to bring up the guided demo lane

#### Scenario: Hosted demo environment distinguishes optional live-provider mode
- **WHEN** an operator enables live-provider or imported real-repository behavior in a hosted demo environment
- **THEN** the project SHALL distinguish those optional provider settings from the minimum guided-demo environment contract

#### Scenario: Hosted demo environment preserves backend-only secret handling
- **WHEN** hosted-demo documentation describes provider keys or repository credentials
- **THEN** it SHALL require those secrets to remain on backend or host-managed surfaces rather than browser-facing configuration

### Requirement: Hosted demo exposes canonical operator health and smoke checks
The system SHALL provide canonical operator-facing checks for a running hosted demo environment so an operator can verify service health and the stable guided walkthrough path without rediscovering ad hoc commands, and those checks SHALL remain distinct from the default offline release baseline.

#### Scenario: Hosted demo health check verifies core services
- **WHEN** an operator runs the hosted-demo health check
- **THEN** the project SHALL verify the expected web, api, and engine service health surfaces and SHALL report failure in an operator-readable way

#### Scenario: Hosted demo smoke check verifies the stable walkthrough
- **WHEN** an operator runs the hosted-demo smoke check against a healthy environment
- **THEN** the project SHALL provide a bounded verification path that confirms the seeded guided demo walkthrough still behaves as the stable public lane

#### Scenario: Hosted demo checks are not confused with the default release gate
- **WHEN** the project documents or runs hosted-demo health and smoke checks
- **THEN** it SHALL identify them as operator-guided hosted validation rather than as a replacement for the default offline release baseline

### Requirement: Hosted demo provides a bounded recovery flow
The system SHALL provide a bounded hosted-demo recovery flow so operators can restore the stable demo lane through reset and reseed actions without rediscovering recovery steps during an incident.

#### Scenario: Operator can reset the seeded demo lane
- **WHEN** the hosted demo workspace becomes unsuitable for a stable walkthrough
- **THEN** the project SHALL provide a reset path that restores the seeded demo lane to a known bounded state

#### Scenario: Operator can reseed after data or migration drift
- **WHEN** the hosted demo environment needs a deeper recovery than a lightweight reset
- **THEN** the project SHALL provide a reseed path that rebuilds the expected demo baseline and identifies the dependencies that must be available first

#### Scenario: Recovery guidance distinguishes reset from reseed
- **WHEN** an operator consults the hosted-demo recovery guidance
- **THEN** the project SHALL explain when a reset is sufficient and when a full reseed is required

### Requirement: Hosted demo preserves demo and imported lane isolation
The system SHALL keep the seeded guided demo lane operationally distinct from imported workspaces in hosted-demo guidance and recovery flows so operators can preserve a stable public walkthrough while separately managing imported real-repository state.

#### Scenario: Hosted operator guidance names the stable demo lane
- **WHEN** an operator follows the hosted-demo guide
- **THEN** the guide SHALL identify the seeded demo workspace as the stable walkthrough lane and SHALL describe imported workspaces as a separate operator-managed lane

#### Scenario: Demo recovery does not implicitly wipe imported workspaces
- **WHEN** an operator uses the default hosted-demo reset path
- **THEN** the recovery flow SHALL restore the seeded demo lane without implicitly deleting imported workspaces unless the operator chooses an explicit broader cleanup action

#### Scenario: Imported checks remain bounded in hosted operation
- **WHEN** hosted-demo guidance references imported real-repository verification
- **THEN** it SHALL describe that path as an operator-guided bounded confidence check rather than as part of the stable public walkthrough

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

### Requirement: Hosted operator guidance covers private access hardening
Hosted operator documentation SHALL describe how to validate and troubleshoot token-backed private repository access without requiring live credentials in default CI.

#### Scenario: Operator validates private access manually
- **WHEN** an operator prepares a hosted preview with private repository access
- **THEN** documentation SHALL identify the setup path, recommended token permission boundary, validation steps, and expected product state

#### Scenario: Operator troubleshoots private access failures
- **WHEN** private repository access fails during lookup, binding, import, sync, or readiness review
- **THEN** documentation SHALL describe likely causes including missing source, unauthorized or revoked token, insufficient permissions, repository not found, provider or network failure, and stale status

#### Scenario: Default CI avoids live private credentials
- **WHEN** release validation runs in default CI or local pre-release mode
- **THEN** private repository access behavior SHALL be validated through deterministic tests rather than requiring live private repository credentials

