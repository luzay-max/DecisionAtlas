## ADDED Requirements

### Requirement: Candidate baseline promotion is controlled
The system SHALL provide an operator-controlled path to promote selected candidate decisions into the accepted baseline.

#### Scenario: Dry-run preview
- **WHEN** the operator runs the candidate baseline promotion without confirmation
- **THEN** the system SHALL report candidate and accepted counts plus the candidate IDs/titles that would be accepted without mutating review state.

#### Scenario: Confirmed accept
- **WHEN** the operator runs the candidate baseline promotion with explicit confirmation and rationale
- **THEN** the system SHALL accept at most the requested bounded number of candidate decisions and include the resulting accepted baseline counts in evidence.

### Requirement: Promotion evidence is auditable
The system SHALL emit bounded JSON and Markdown evidence for accepted baseline promotion.

#### Scenario: Evidence is generated
- **WHEN** accepted baseline promotion completes in dry-run or confirmed mode
- **THEN** the evidence SHALL include mode, workspace slug, before/after counts, selected decision IDs/titles, rationale, status, and limitations without embedding secrets or raw private source.

#### Scenario: Review API fails
- **WHEN** a review mutation fails
- **THEN** the evidence SHALL report warning or blocking status with bounded error details and preserve the before counts.
