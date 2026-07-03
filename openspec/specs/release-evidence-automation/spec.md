# release-evidence-automation Specification

## Purpose
Generates machine-readable release evidence bundles and operator-readable Markdown handoffs that separate required release gates from advisory confidence signals.
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

### Requirement: Release evidence can be referenced by hosted readiness
Generated release evidence bundles SHALL be usable as referenced input for hosted/operator readiness records without changing release gate semantics.

#### Scenario: Hosted readiness consumes release evidence reference
- **WHEN** a hosted readiness record includes a release evidence bundle
- **THEN** the hosted readiness record SHALL show the release evidence status and source path
- **AND** it SHALL keep hosted readiness classification separate from canonical release validation.

#### Scenario: Release evidence warning remains disclosed
- **WHEN** a referenced release evidence bundle reports warning, caution, missing input, or advisory blockers
- **THEN** hosted readiness output SHALL disclose that status rather than treating the bundle as clean pass.

### Requirement: Release evidence can be archived into readiness history
Generated release evidence bundles SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Release evidence is archived
- **WHEN** an operator archives readiness evidence with a release evidence JSON path
- **THEN** the history entry SHALL preserve the release evidence overall status, required gate statuses, advisory signal statuses, warnings, missing inputs, and source artifact filename.

#### Scenario: Release evidence is absent
- **WHEN** readiness history is archived without release evidence
- **THEN** the history entry SHALL record release evidence as not provided rather than passed.

### Requirement: Release evidence can be orchestrated by release rehearsal
Release evidence automation SHALL be usable as a lane in the one-command release rehearsal bundle.

#### Scenario: Release evidence JSON is provided
- **WHEN** a release evidence JSON path is supplied to the rehearsal command
- **THEN** the rehearsal SHALL include its status, summary, and evidence path.

#### Scenario: Release evidence is not provided
- **WHEN** release evidence is omitted
- **THEN** the rehearsal SHALL preserve the release lane as `not_provided` or run it only when explicitly requested.
