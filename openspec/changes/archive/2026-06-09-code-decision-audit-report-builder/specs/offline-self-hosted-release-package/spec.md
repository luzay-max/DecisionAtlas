## ADDED Requirements

### Requirement: Self-hosted pilots can generate Code Decision Audit reports
Self-hosted delivery materials SHALL reference a local Code Decision Audit report generation path for paid pilots and customer evaluations.

#### Scenario: Paid pilot handoff is prepared
- **WHEN** an operator prepares a self-hosted paid pilot or customer evaluation
- **THEN** documentation MUST point to the audit report builder and required/optional evidence inputs

#### Scenario: Audit report evidence is incomplete
- **WHEN** optional evidence inputs are missing
- **THEN** documentation MUST instruct operators to disclose `not_provided` or `operator_guided` states rather than treating them as pass
