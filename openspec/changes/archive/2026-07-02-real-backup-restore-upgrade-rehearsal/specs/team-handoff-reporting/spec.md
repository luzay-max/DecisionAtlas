## ADDED Requirements

### Requirement: Handoff report references real continuity rehearsal
Team handoff reports SHALL disclose real backup/restore/upgrade rehearsal evidence when provided.

#### Scenario: Real continuity evidence is included
- **WHEN** handoff report generation receives real continuity rehearsal evidence
- **THEN** the report SHALL summarize continuity status, scratch scope, restore validation status, post-upgrade status, rollback plan status, blockers, limitations, and recommended next actions

#### Scenario: Real continuity evidence is missing
- **WHEN** handoff report generation does not receive real continuity rehearsal evidence
- **THEN** the report SHALL mark tested continuity evidence as `not_provided` or `operator_guided` rather than omitting the section

#### Scenario: Real continuity evidence contains sensitive material
- **WHEN** real continuity evidence includes raw backups, `.env` secrets, credential material, private source content, or unbounded local logs
- **THEN** handoff report generation SHALL reject the evidence or preserve a `blocking` status without copying sensitive content into the report
