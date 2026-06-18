## ADDED Requirements

### Requirement: Self-hosted delivery rehearsal includes continuity evidence
The self-hosted delivery rehearsal SHALL include backup/restore/upgrade rehearsal evidence before claiming customer trial or paid handoff continuity readiness.

#### Scenario: Continuity evidence is available
- **WHEN** self-hosted delivery rehearsal evidence is prepared for customer handoff
- **THEN** it SHALL reference backup/restore/upgrade rehearsal JSON or Markdown evidence.

#### Scenario: Continuity evidence is missing
- **WHEN** backup/restore/upgrade rehearsal evidence is absent
- **THEN** delivery rehearsal material SHALL preserve `operator_guided` or `not_provided` state and avoid claiming clean continuity readiness.
