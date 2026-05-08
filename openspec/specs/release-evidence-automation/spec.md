# release-evidence-automation Specification

## Purpose
TBD - created by archiving change release-evidence-automation. Update Purpose after archive.
## Requirements
### Requirement: Release evidence bundle generation
The system SHALL provide a local way to generate a release evidence bundle that summarizes release readiness signals in a machine-readable format.

#### Scenario: Generate machine-readable evidence
- **WHEN** an operator runs the release evidence command with supported inputs
- **THEN** the system SHALL write a JSON evidence bundle
- **AND** the bundle SHALL include generation metadata, source paths, required gate summaries, advisory signal summaries, missing inputs, and warnings.

#### Scenario: Optional evidence is missing
- **WHEN** an optional evidence input is not provided
- **THEN** the system SHALL record that input as missing or not provided
- **AND** the system SHALL NOT silently report the missing optional evidence as passed.

### Requirement: Mandatory and advisory signal separation
The system SHALL distinguish required release gates from advisory confidence signals in generated release evidence.

#### Scenario: Required gate fails
- **WHEN** a required release gate is reported as failed
- **THEN** the generated evidence SHALL mark the required gate as failed
- **AND** the overall release status SHALL NOT claim clean readiness.

#### Scenario: Advisory guardrail returns caution
- **WHEN** a governance guardrail or protocol status reports a caution-level result
- **THEN** the generated evidence SHALL disclose the caution as an advisory signal
- **AND** the generated evidence SHALL preserve whether the advisory signal would block under the reported policy.

#### Scenario: Optional benchmark comparison reports a blocker
- **WHEN** an optional real-repo benchmark comparison reports an operational blocker
- **THEN** the generated evidence SHALL disclose the blocker in advisory or benchmark sections
- **AND** the generated evidence SHALL NOT treat the blocker as a default canonical gate failure unless explicitly configured by future policy.

### Requirement: Explicit source inputs
The system SHALL consume optional release evidence from explicit source paths rather than broad implicit temporary-file discovery.

#### Scenario: Operator provides benchmark comparison path
- **WHEN** the operator provides a real-repo benchmark comparison report path
- **THEN** the system SHALL load evidence from that path
- **AND** the generated bundle SHALL record the path used.

#### Scenario: Source path is invalid
- **WHEN** the operator provides a source path that does not exist or cannot be parsed
- **THEN** the system SHALL report a clear warning or error for that source
- **AND** the generated evidence SHALL NOT treat that source as passed.

### Requirement: Markdown handoff output
The system SHALL generate an operator-readable Markdown handoff from the release evidence bundle.

#### Scenario: Markdown handoff is generated
- **WHEN** release evidence generation completes
- **THEN** the system SHALL write a Markdown summary
- **AND** the Markdown SHALL include required gates, advisory signals, benchmark evidence, missing inputs, warnings, and source paths.

#### Scenario: Markdown mirrors JSON status
- **WHEN** the JSON bundle reports warnings, missing inputs, or advisory cautions
- **THEN** the Markdown handoff SHALL present those same statuses without hiding them.

### Requirement: Non-mutating local operation
The system SHALL keep release evidence generation local and non-mutating by default.

#### Scenario: Generate release evidence
- **WHEN** the operator runs the release evidence command
- **THEN** the command SHALL NOT create git tags, push commits, publish releases, update archived changes, or require network access by default.

