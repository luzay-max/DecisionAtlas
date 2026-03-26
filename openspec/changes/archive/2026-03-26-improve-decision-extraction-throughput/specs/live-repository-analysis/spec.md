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
