## Purpose

Validates whether sanitized external/customer-controlled host trial evidence is strong enough for release or customer handoff claims, while preserving template, placeholder, local-only, warning, and blocking boundaries.

## Requirements

### Requirement: Real external host trial evidence is generated
The system SHALL generate bounded real external host trial evidence from explicit sanitized host input and selected source evidence artifacts.

#### Scenario: Trial evidence is generated
- **WHEN** an operator runs the real external host trial evidence collector with output paths
- **THEN** the system SHALL write JSON and Markdown evidence containing schema version, generated timestamp, label, status, host proof level, lane summaries, placeholder findings, redaction findings, limitations, and recommended next actions.

#### Scenario: Source evidence is supplied
- **WHEN** customer-host v2 or full-chain random repo release evidence paths are supplied
- **THEN** the collector SHALL preserve source status, selected repository identifiers, lane counts, blockers, and limitations without converting warnings into pass.

### Requirement: Placeholder and template evidence remains non-clean
The system SHALL detect sample templates and placeholder values before allowing real external host trial evidence to pass.

#### Scenario: Example template is used
- **WHEN** the host input contains placeholder values such as `fill-me`, `customer-or-operator-name`, `optional`, sample limitations, or template markers
- **THEN** the real external host trial evidence SHALL be `warning` or `operator_guided`
- **AND** it SHALL list the placeholder findings and state that real external/customer-controlled host proof is still missing.

#### Scenario: Required host fields are missing
- **WHEN** host class, operating system family, deployment mode, package version, commit, operator, customer-control acknowledgement, redaction acknowledgement, or browser smoke status is missing
- **THEN** the collector SHALL keep the affected lane non-clean and include a recommended next action.

### Requirement: Real external host trial evidence is safe to archive
The system SHALL prevent obvious sensitive material from being recorded in real external host trial evidence.

#### Scenario: Secret marker is detected
- **WHEN** host input or source evidence contains obvious token, private key, `.env` secret assignment, raw private repository content, or raw backup material
- **THEN** the collector SHALL mark the evidence `blocking`
- **AND** generated Markdown SHALL NOT include the raw sensitive value.

#### Scenario: Collector runs
- **WHEN** the collector runs
- **THEN** it SHALL NOT run installs, imports, browsers, Docker, migrations, git push, package publishing, or customer infrastructure mutations by default.

### Requirement: Real external host trial evidence can be archived
The system SHALL allow real external host trial evidence to be archived into readiness evidence history when requested.

#### Scenario: Archive is requested
- **WHEN** the operator enables readiness-history archival
- **THEN** the generated real external host trial JSON and Markdown SHALL be copied into a dated or labeled readiness history entry.

#### Scenario: Archive is skipped
- **WHEN** archival is not requested
- **THEN** the collector SHALL still write `.tmp` JSON and Markdown and expose archival as a next recommended action.
