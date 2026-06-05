## Purpose

Allow long-running repository imports to be paused and resumed without losing progress or forcing operators to restart completed work.

## Requirements

### Requirement: Import job pausing
The system SHALL allow users to pause a running import job without losing progress.

#### Scenario: User pauses a running import
- **WHEN** the user triggers the pause action on an active import job
- **THEN** the system SHALL suspend background extraction tasks and mark the job status as paused
- **THEN** the system SHALL maintain the current extraction progress

### Requirement: Import job resuming
The system SHALL allow users to resume a previously paused import job.

#### Scenario: User resumes a paused import
- **WHEN** the user triggers the resume action on a paused import job
- **THEN** the system SHALL restore the background extraction tasks and mark the job status as running
- **THEN** the system SHALL continue from the exact progress state when it was paused
