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

### Requirement: Hosted preview defines a pre-demo readiness checklist
The system SHALL define a concise hosted preview readiness checklist that an operator can run before externally demonstrating the v0.3 RC baseline.

#### Scenario: Checklist names minimum hosted conditions
- **WHEN** an operator prepares an external hosted preview
- **THEN** the checklist SHALL identify required service health, seeded demo data readiness, browser smoke coverage, reset/reseed recovery status, and known limitations

#### Scenario: Checklist separates stable and optional lanes
- **WHEN** the checklist describes what can be shown during the preview
- **THEN** it SHALL distinguish the stable seeded guided demo lane from optional imported repository, GitHub App, and private repository operator/admin lanes

#### Scenario: Checklist records pass and limitation state
- **WHEN** an operator completes hosted preview readiness checks
- **THEN** the checklist or report SHALL record pass, blocking failure, non-blocking failure, or known limitation for each relevant lane

### Requirement: Hosted preview provides an external walkthrough script
The system SHALL provide a bounded external walkthrough script for hosted preview demonstrations.

#### Scenario: Walkthrough starts with guided demo
- **WHEN** an operator follows the external walkthrough script
- **THEN** it SHALL start with the seeded guided demo workspace and preserve the dashboard, review, why, timeline, and drift order

#### Scenario: Walkthrough frames advanced lanes correctly
- **WHEN** the walkthrough mentions imported real repositories, GitHub App sync, or private repository access
- **THEN** it SHALL frame those lanes as optional operator/admin capabilities with provider, credential, and network dependencies

### Requirement: Hosted preview recovery drill is documented
The system SHALL document and, when possible, rehearse hosted preview recovery steps before external demonstration.

#### Scenario: Reset drill restores seeded lane
- **WHEN** an operator runs the hosted preview reset drill
- **THEN** the documented path SHALL restore the seeded demo lane without implicitly deleting imported workspaces

#### Scenario: Reseed drill explains deeper recovery
- **WHEN** reset is insufficient because migrations or data drift affected the seeded lane
- **THEN** the documented path SHALL explain when and how to run the reseed operation

### Requirement: Seeded demo recovery restores guided walkthrough state
The system SHALL define seeded demo recovery as restoring the stable guided demo lane to a known walkthrough-ready state that includes the demo workspace, accepted decision baseline, reviewable candidate queue, source-backed why-search path, timeline history, and drift alert path.

#### Scenario: Reset restores consumed review queue
- **WHEN** the seeded demo review queue has been consumed before an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore at least one reviewable candidate decision for the guided demo workspace

#### Scenario: Reset restores source-backed accepted baseline
- **WHEN** an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore accepted demo decisions with source references sufficient for why-search and timeline walkthroughs

#### Scenario: Reset restores drift walkthrough state
- **WHEN** an operator runs the seeded demo reset path
- **THEN** the recovery flow SHALL restore the seeded drift alert state needed for the guided drift walkthrough

### Requirement: Seeded demo recovery preserves imported workspace lane
The system SHALL keep seeded demo recovery scoped to the stable `demo-workspace` lane and SHALL NOT implicitly delete imported real-repository workspaces.

#### Scenario: Imported workspaces survive seeded reset
- **WHEN** an imported workspace exists and an operator runs the default seeded demo reset path
- **THEN** the imported workspace SHALL remain available after the seeded demo lane is restored

#### Scenario: Recovery docs name the destructive boundary
- **WHEN** hosted operator guidance describes demo reset or reseed
- **THEN** it SHALL state that the default recovery path is scoped to `demo-workspace` and does not perform broad imported-workspace cleanup

### Requirement: Seeded demo readiness can be verified
The system SHALL provide an operator-readable way to verify whether the seeded guided demo lane is ready for a walkthrough after startup, reset, or reseed.

#### Scenario: Readiness verifies required demo state
- **WHEN** an operator checks seeded demo readiness
- **THEN** the result SHALL indicate whether the demo workspace, accepted decisions, candidate queue, source references, timeline path, and drift alert path are present

#### Scenario: Readiness reports recovery guidance
- **WHEN** seeded demo readiness fails
- **THEN** the result SHALL identify whether reset or reseed is the recommended recovery path

### Requirement: Hosted preview includes governed readiness checks
The system SHALL define governed hosted preview readiness checks that cover the stable demo lane, governance demo lane, guardrail advisory state, recovery path, and optional real-repository credibility evidence without making those checks part of the default release gate.

#### Scenario: Governed checklist names required and optional lanes
- **WHEN** an operator prepares a governed hosted preview
- **THEN** the readiness checklist SHALL distinguish required stable guided-demo checks from optional governance, imported repository, GitHub App, private repository, and real-repository benchmark checks

#### Scenario: Governance smoke is part of operator readiness
- **WHEN** the checklist includes the governance lane
- **THEN** it SHALL identify the commands or product surfaces used to verify governance Markdown ingest, rule draft review, accepted-rule visibility, and agent guardrail summary behavior

#### Scenario: Readiness classification remains bounded
- **WHEN** an operator records governed hosted preview readiness
- **THEN** each lane SHALL be classified as pass, blocking, non-blocking, known limitation, or operator-guided rather than hidden behind a single readiness score

### Requirement: Hosted preview documents governed recovery and handoff
The system SHALL document how operators recover the stable demo lane and how they record governance guardrail evidence before externally demonstrating the governed preview.

#### Scenario: Recovery remains scoped to stable demo
- **WHEN** hosted preview recovery guidance mentions reset or reseed
- **THEN** it SHALL state that default recovery restores `demo-workspace` and does not implicitly delete imported workspaces or governance history

#### Scenario: Guardrail evidence is recorded before handoff
- **WHEN** an operator runs the agent governance guardrail before a governed hosted preview
- **THEN** the readiness record SHALL include the guardrail status and any caution or pause evidence that affects the preview

#### Scenario: Blocking readiness stops public walkthrough
- **WHEN** governed readiness finds a blocking issue in web, API, engine, seeded demo data, or walkthrough smoke
- **THEN** the operator guidance SHALL identify that the external public walkthrough should not proceed until the issue is resolved or explicitly excluded
