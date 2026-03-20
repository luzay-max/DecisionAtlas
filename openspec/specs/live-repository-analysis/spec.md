# live-repository-analysis Specification

## Purpose
TBD - created by archiving change harden-live-repo-analysis. Update Purpose after archive.

## Requirements
### Requirement: Users can start live analysis for a public GitHub repository
The system SHALL allow a user to submit a public GitHub repository reference and start a one-off live analysis run against that repository.

#### Scenario: Start live analysis from owner and repo reference
- **WHEN** the user submits a valid public repository reference such as `owner/repo`
- **THEN** the system SHALL create or reuse an imported workspace for that repository and queue a live analysis job for that workspace

#### Scenario: Start live analysis from GitHub URL
- **WHEN** the user submits a valid public GitHub repository URL
- **THEN** the system SHALL normalize the URL to its repository identity and start the same live analysis flow as an `owner/repo` submission

### Requirement: Live analysis stays separate from the guided demo workspace
The system SHALL keep live-analysis repository runs isolated from the guided demo workspace so seeded walkthrough data is not mixed into arbitrary public repository analysis.

#### Scenario: Live analysis uses an imported workspace
- **WHEN** the user starts analysis for a public repository other than the guided demo repository
- **THEN** the system SHALL route the run into an imported workspace that does not rely on seeded demo artifacts

#### Scenario: Repeated analysis reuses repository workspace identity
- **WHEN** the user starts live analysis for a repository that already has an imported workspace
- **THEN** the system SHALL reuse that workspace identity rather than creating a duplicate workspace for the same normalized repository

### Requirement: Live analysis exposes stage-aware job progress
The system SHALL expose stage-aware live-analysis progress so users can tell which part of the pipeline is currently running.

#### Scenario: Job reports pipeline stage while running
- **WHEN** a live analysis job is still in progress
- **THEN** the system SHALL report a stage such as queued, artifact import, indexing, or decision extraction instead of only a generic running state

#### Scenario: Job reports terminal stage on completion
- **WHEN** a live analysis job reaches a terminal state
- **THEN** the system SHALL report whether the run succeeded or failed and SHALL preserve the final stage summary for later inspection

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, and operational failure so users can interpret live-analysis results correctly.

#### Scenario: Thin repository yields insufficient evidence
- **WHEN** a live analysis job completes but produces few or no candidate decisions because the repository lacks enough decision evidence
- **THEN** the system SHALL surface that outcome as insufficient evidence rather than implying the pipeline failed

#### Scenario: Runtime failure yields explicit failure context
- **WHEN** a live analysis job fails because of provider, network, or import execution errors
- **THEN** the system SHALL expose a failure summary that identifies the failing stage and broad failure category
