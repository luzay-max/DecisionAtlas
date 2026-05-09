## ADDED Requirements

### Requirement: Hosted readiness can be archived into readiness history
Generated hosted/operator readiness artifacts SHALL be usable as explicit input to readiness evidence history.

#### Scenario: Hosted readiness is archived
- **WHEN** an operator archives readiness evidence with a hosted readiness JSON path
- **THEN** the history entry SHALL preserve the hosted readiness overall status, public walkthrough status, public walkthrough decision, blockers, operator-guided lanes, known limitations, and source artifact filename.

#### Scenario: Hosted readiness is absent
- **WHEN** readiness history is archived without hosted readiness evidence
- **THEN** the history entry SHALL record hosted readiness as not provided rather than passed.
