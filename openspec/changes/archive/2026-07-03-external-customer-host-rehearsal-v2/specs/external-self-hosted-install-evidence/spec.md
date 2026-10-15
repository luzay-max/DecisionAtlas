## ADDED Requirements

### Requirement: External install evidence can feed customer-host v2 rehearsal
External self-hosted install evidence SHALL be usable as a source lane for customer-host v2 rehearsal.

#### Scenario: External evidence is supplied to v2 rehearsal
- **WHEN** customer-host v2 rehearsal receives external install evidence JSON or Markdown
- **THEN** it SHALL preserve the external evidence status, host class, blockers, and limitations as a source lane.

#### Scenario: External evidence is missing from v2 rehearsal
- **WHEN** customer-host v2 rehearsal runs without external install evidence
- **THEN** it SHALL mark the external install lane `not_provided` or `operator_guided` and SHALL NOT claim customer-controlled install proof.
