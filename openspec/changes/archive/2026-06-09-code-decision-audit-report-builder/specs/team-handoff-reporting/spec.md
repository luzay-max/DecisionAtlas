## ADDED Requirements

### Requirement: Team handoff can feed Code Decision Audit reports
Team handoff reports SHALL be usable as source evidence for customer-readable Code Decision Audit reports.

#### Scenario: Handoff evidence is supplied
- **WHEN** a team handoff JSON path is provided to the Code Decision Audit report builder
- **THEN** the audit report MUST summarize handoff status, workspace/repository scope, and source evidence states

#### Scenario: Handoff evidence is omitted
- **WHEN** handoff evidence is not supplied
- **THEN** the audit report MUST preserve handoff evidence as `not_provided`
