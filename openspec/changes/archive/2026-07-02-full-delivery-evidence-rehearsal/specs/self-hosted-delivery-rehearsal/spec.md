## ADDED Requirements

### Requirement: Delivery rehearsal archives complete evidence history
The self-hosted delivery rehearsal SHALL include guidance for archiving complete delivery evidence into readiness history.

#### Scenario: Complete evidence is available
- **WHEN** release, hosted, benchmark, external install, real continuity, handoff, and audit evidence artifacts exist
- **THEN** the rehearsal documentation SHALL provide a command that archives those artifacts into readiness history and regenerates index/trend output

#### Scenario: Evidence is incomplete
- **WHEN** some complete delivery evidence artifacts are missing
- **THEN** the rehearsal guidance SHALL require the archive to preserve missing evidence as `not_provided`, `operator_guided`, `warning`, or `blocking`
