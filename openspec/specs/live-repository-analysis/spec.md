## MODIFIED Requirements

### Requirement: Live analysis exposes stage-aware job progress
The system SHALL expose stage-aware live-analysis progress so users can tell which part of the pipeline is currently running and whether long-running extraction work is making real progress.

#### Scenario: Job reports pipeline stage while running
- **WHEN** a live analysis job is still in progress
- **THEN** the system SHALL report a stage such as queued, artifact import, indexing, or decision extraction instead of only a generic running state

#### Scenario: Decision extraction stage reports detailed progress
- **WHEN** a live analysis job is in the decision extraction stage
- **THEN** the system SHALL expose detailed extraction progress including processed work, total planned work, and ETA-friendly summary fields

#### Scenario: Job reports terminal stage on completion
- **WHEN** a live analysis job reaches a terminal state
- **THEN** the system SHALL report whether the run succeeded or failed and SHALL preserve the final stage summary for later inspection

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, and imported-workspace readiness so users can interpret live-analysis results correctly and know the strongest next action.

#### Scenario: Thin repository yields insufficient evidence
- **WHEN** a live analysis job completes but produces few or no candidate decisions because the repository lacks enough decision evidence
- **THEN** the system SHALL surface that outcome as insufficient evidence rather than implying the pipeline failed

#### Scenario: Review-ready workspace yields actionable outcome
- **WHEN** a live analysis job completes and the imported workspace contains reviewable candidate decisions
- **THEN** the system SHALL expose enough outcome context for the product to recommend review as the next action

#### Scenario: Runtime failure yields explicit failure context
- **WHEN** a live analysis job fails because of provider, network, or import execution errors
- **THEN** the system SHALL expose a failure summary that identifies the failing stage and broad failure category
