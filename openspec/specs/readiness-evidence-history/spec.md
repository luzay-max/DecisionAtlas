# readiness-evidence-history Specification

## Purpose
TBD - created by archiving change readiness-evidence-history. Update Purpose after archive.
## Requirements
### Requirement: Readiness evidence can be archived into durable history
The system SHALL provide a local way to promote selected readiness evidence artifacts from scratch output into a durable dated or versioned history entry.

#### Scenario: Archive selected evidence artifacts
- **WHEN** an operator provides explicit source paths for release evidence, hosted readiness evidence, and benchmark comparison evidence
- **THEN** the system SHALL copy the selected artifacts into a dated or versioned history entry
- **AND** the history entry SHALL record source paths, generated timestamps when available, statuses, warnings, blockers, and benchmark movement counts.

#### Scenario: Evidence source is omitted
- **WHEN** an optional evidence source path is not provided during history archiving
- **THEN** the history entry SHALL record that evidence family as not provided
- **AND** the system SHALL NOT silently search `.tmp` for a substitute artifact.

### Requirement: Readiness evidence history maintains an index
The system SHALL maintain a machine-readable index of archived readiness evidence entries.

#### Scenario: Index records evidence entry summary
- **WHEN** a readiness evidence entry is archived
- **THEN** the history index SHALL include the entry id, label, created timestamp, commit or version label when provided, evidence family statuses, warning counts, blocker counts, operator-guided counts, and benchmark regression or operational blocker counts when available.

#### Scenario: Index remains deterministic
- **WHEN** the history index is regenerated
- **THEN** entries SHALL be sorted deterministically by date and entry id
- **AND** the index SHALL be reproducible from the archived entry summaries.

### Requirement: Readiness evidence history provides trend summaries
The system SHALL provide an offline trend summary across archived readiness evidence entries.

#### Scenario: Compare recent evidence entries
- **WHEN** an operator requests a trend summary
- **THEN** the system SHALL summarize release status movement, hosted readiness movement, benchmark regression counts, benchmark operational blocker counts, warning counts, and not-provided or operator-guided evidence counts across recent entries.

#### Scenario: Trend summary preserves non-clean states
- **WHEN** archived evidence includes warning, blocking, operator-guided, known-limitation, or not-provided states
- **THEN** the trend summary SHALL disclose those states rather than converting them into pass.

### Requirement: Readiness evidence history remains local and non-mutating
The system SHALL keep evidence history archiving local and non-mutating except for writing the explicit history files.

#### Scenario: Archive evidence history
- **WHEN** an operator archives readiness evidence
- **THEN** the command SHALL NOT run pre-release, hosted health checks, hosted smoke checks, reset, reseed, live benchmark, imports, git push, release publishing, or OpenSpec archive actions by default.

#### Scenario: Sensitive material is excluded
- **WHEN** documentation describes readiness evidence history
- **THEN** it SHALL warn operators not to archive secrets, private repository contents, raw model output, or unnecessary local-only logs.

### Requirement: Readiness evidence history supports human handoff
The system SHALL generate or update an operator-readable history summary suitable for release, preview, or project update handoff.

#### Scenario: Markdown history summary is generated
- **WHEN** evidence history is archived or summarized
- **THEN** the system SHALL produce a Markdown summary that lists entries, linked artifact filenames, statuses, warnings, blockers, benchmark movement counts, and recommended follow-up.

### Requirement: Readiness history can represent self-hosted rehearsal checkpoints
The system SHALL allow readiness evidence history to represent a self-hosted delivery rehearsal checkpoint.

#### Scenario: Rehearsal evidence is archived
- **WHEN** an operator archives evidence from a self-hosted delivery rehearsal
- **THEN** the history entry SHALL be able to identify the entry as a self-hosted rehearsal
- **AND** it SHALL link or list the release evidence, hosted/operator readiness evidence, benchmark comparison evidence, and rehearsal handoff summary when provided.

#### Scenario: Rehearsal trend is reviewed
- **WHEN** an operator reviews readiness history trends
- **THEN** self-hosted rehearsal entries SHALL preserve warning, blocking, operator-guided, known-limitation, and not-provided counts
- **AND** the trend summary SHALL NOT convert those states into pass.

### Requirement: Readiness evidence history can feed team handoff reports
The system SHALL allow archived readiness evidence entries to be referenced as source material for team handoff reports.

#### Scenario: Handoff report references readiness history
- **WHEN** an operator provides a readiness evidence history entry or index to handoff report generation
- **THEN** the handoff report SHALL include the selected entry id, label, evidence family statuses, warning counts, blocker counts, operator-guided counts, benchmark movement counts, and linked artifact filenames

#### Scenario: History state is preserved
- **WHEN** readiness history includes warning, blocking, not-provided, known-limitation, or operator-guided states
- **THEN** the handoff report SHALL preserve those states and SHALL NOT summarize the readiness history as clean pass

### Requirement: Readiness materials can reference benchmark trend evidence
Readiness evidence workflows SHALL allow operators to attach benchmark trend evidence alongside release evidence, hosted readiness, and benchmark comparison evidence.

#### Scenario: Trend evidence exists for a release rehearsal
- **WHEN** benchmark trend evidence is generated for a release rehearsal
- **THEN** readiness-facing Markdown or handoff summaries MUST expose the trend status and recommended follow-up without replacing the benchmark comparison artifact

#### Scenario: Trend evidence is missing
- **WHEN** benchmark trend evidence is not supplied
- **THEN** readiness-facing summaries MUST keep the missing trend evidence visible as `not_provided` or `warning` rather than silently dropping it
