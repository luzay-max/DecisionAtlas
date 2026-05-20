## ADDED Requirements

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
