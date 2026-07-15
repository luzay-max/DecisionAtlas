## MODIFIED Requirements

### Requirement: Real external host trial evidence is generated
The system SHALL generate bounded real external host trial evidence from explicit sanitized host input and selected source evidence artifacts, including package, startup, health, administrator login, team/workspace setup, repository import, review, Why, Drift, continuity, browser smoke, and redaction lane summaries when those lanes are applicable.

#### Scenario: Trial evidence is generated
- **WHEN** an operator runs the real external host trial evidence collector with output paths
- **THEN** the system SHALL write JSON and Markdown evidence containing schema version, generated timestamp, label, status, host proof level, lane summaries, placeholder findings, redaction findings, limitations, and recommended next actions.

#### Scenario: Core lane is omitted
- **WHEN** a supplied host input does not contain an applicable core lane
- **THEN** the collector SHALL represent that lane as `not_provided` or `operator_guided` with a rerun condition
- **AND** it SHALL not infer a pass from another lane.

#### Scenario: Source evidence is supplied
- **WHEN** customer-host v2 or full-chain random repo release evidence paths are supplied
- **THEN** the collector SHALL preserve source status, selected repository identifiers, lane counts, blockers, and limitations without converting warnings into pass.

### Requirement: External host evidence is archive-safe
The system SHALL prevent secrets, raw private material, and unbounded local paths from being recorded in real external host trial evidence.

#### Scenario: External source path is supplied
- **WHEN** a source or host input path is outside the repository root
- **THEN** JSON, Markdown, warnings, and readiness-history references SHALL use `<external-path>` or another bounded redaction
- **AND** SHALL NOT include an absolute drive path or home directory.

#### Scenario: Secret marker is detected
- **WHEN** host input or source evidence contains an obvious token, private key, `.env` secret assignment, raw private repository content, or raw backup material
- **THEN** the collector SHALL mark the evidence `blocking`
- **AND** generated Markdown SHALL NOT include the raw sensitive value.
