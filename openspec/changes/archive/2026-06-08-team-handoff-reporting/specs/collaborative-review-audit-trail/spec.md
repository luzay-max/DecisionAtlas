## ADDED Requirements

### Requirement: Audit history can feed team handoff reports
The system SHALL provide compact audit history summaries suitable for team handoff reporting.

#### Scenario: Handoff report includes review history
- **WHEN** handoff report generation receives audit history for decisions, governance rules, or drift alerts
- **THEN** the report SHALL summarize actor display name or username, role, target type, action, state transition, rationale when present, and timestamp

#### Scenario: Handoff audit summary remains bounded
- **WHEN** audit history is included in a handoff report
- **THEN** the report SHALL include compact recent or representative history and SHALL NOT expose raw tokens, credential material, unrelated owner scopes, or unbounded rationale text
