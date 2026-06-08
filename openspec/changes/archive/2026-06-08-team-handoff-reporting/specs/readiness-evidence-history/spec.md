## ADDED Requirements

### Requirement: Readiness evidence history can feed team handoff reports
The system SHALL allow archived readiness evidence entries to be referenced as source material for team handoff reports.

#### Scenario: Handoff report references readiness history
- **WHEN** an operator provides a readiness evidence history entry or index to handoff report generation
- **THEN** the handoff report SHALL include the selected entry id, label, evidence family statuses, warning counts, blocker counts, operator-guided counts, benchmark movement counts, and linked artifact filenames

#### Scenario: History state is preserved
- **WHEN** readiness history includes warning, blocking, not-provided, known-limitation, or operator-guided states
- **THEN** the handoff report SHALL preserve those states and SHALL NOT summarize the readiness history as clean pass
