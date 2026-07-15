# customer-host-trial-operator-kit Specification

## Purpose
TBD - created by archiving change complete-real-customer-host-trial. Update Purpose after archive.
## Requirements
### Requirement: Customer host trial input is versioned and sanitized
The system SHALL define a versioned operator input contract for a self-hosted customer-host trial with host profile, package identity, redaction acknowledgement, and bounded lane records.

#### Scenario: Operator prepares a trial input
- **WHEN** an operator records a trial on a clean or customer-controlled host
- **THEN** the input SHALL identify host class, operating system family, deployment mode, operator, package version or commit, and whether the host is customer-controlled
- **AND** it SHALL record redaction acknowledgement without containing credentials, raw logs, private source, or raw backups.

#### Scenario: Existing v2 input is reused
- **WHEN** an operator supplies an existing customer-host v2 input that lacks the new optional lanes
- **THEN** the collector SHALL accept the input and classify missing lanes as `not_provided` or `operator_guided` rather than failing schema parsing.

### Requirement: Core delivery lanes are explicit
The operator kit SHALL define bounded lane identifiers for startup, health, administrator login, team/workspace setup, repository import, review, Why, Drift, continuity, and browser smoke.

#### Scenario: Trial is partially completed
- **WHEN** only some core lanes have been exercised
- **THEN** each omitted lane SHALL remain visible with `not_provided` or `operator_guided` status and a rerun action
- **AND** the summary SHALL distinguish omitted work from a failed lane.

#### Scenario: Lane summary is recorded
- **WHEN** a lane is marked pass, warning, blocking, operator-guided, or not-provided
- **THEN** the input SHALL contain only a bounded status and short sanitized summary, not raw command output or source content.

### Requirement: Operator checklist is non-destructive
The kit SHALL provide an ordered checklist and commands for package verification, startup, health, login, team/workspace setup, repository import, core review flow, continuity check, and evidence archival.

#### Scenario: Operator runs the checklist
- **WHEN** the checklist is followed on a target host
- **THEN** it SHALL identify expected evidence output paths and the owner of each manual step
- **AND** the collector SHALL not automatically install, start, import, migrate, upload, or mutate customer infrastructure.

### Requirement: Trial proof level is honest
The kit SHALL classify trial proof separately from overall status.

#### Scenario: Customer-controlled trial is clean
- **WHEN** the host is explicitly customer-controlled, values are non-template, browser smoke passes, and all required core lanes pass
- **THEN** proof level SHALL be `real_external_customer_controlled`.

#### Scenario: Local or template rehearsal is supplied
- **WHEN** the input is from the developer workstation, local Docker, or an example/template
- **THEN** proof level SHALL remain `operator_guided`, `template_or_placeholder`, or another non-clean classification
- **AND** the report SHALL not claim customer-host readiness.

### Requirement: Trial evidence can be archived
The kit SHALL integrate with the existing readiness-history archive and preserve the trial's status, proof level, lane summaries, limitations, and next actions.

#### Scenario: Operator requests archival
- **WHEN** the collector is run with archival enabled
- **THEN** it SHALL write a dated or labeled readiness-history entry containing JSON and Markdown trial evidence and update the existing index/trend output.

#### Scenario: Archival input is incomplete
- **WHEN** release, hosted, benchmark, continuity, or handoff evidence is absent
- **THEN** the archived entry SHALL preserve the missing state and SHALL NOT upgrade the trial proof level.

