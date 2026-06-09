## ADDED Requirements

### Requirement: Handoff report references clean install rehearsal
Team handoff reports SHALL disclose clean install rehearsal evidence when provided.

#### Scenario: Clean install evidence is included
- **WHEN** handoff report generation receives clean install rehearsal evidence
- **THEN** the report SHALL summarize clean install status, package path, clean workspace path, evidence family statuses, blockers, limitations, and recommended next actions

#### Scenario: Clean install evidence is missing
- **WHEN** handoff report generation does not receive clean install rehearsal evidence
- **THEN** the report SHALL mark the clean install rehearsal section as `not_provided` or `operator_guided` rather than omitting it
