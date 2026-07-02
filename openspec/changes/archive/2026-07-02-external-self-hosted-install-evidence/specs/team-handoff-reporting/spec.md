## ADDED Requirements

### Requirement: Handoff report references external install evidence
Team handoff reports SHALL disclose external or customer-controlled host install evidence when provided.

#### Scenario: External install evidence is included
- **WHEN** handoff report generation receives external install evidence
- **THEN** the report SHALL summarize external install status, host class, package identity, lane statuses, blockers, limitations, and recommended next actions

#### Scenario: External install evidence is missing
- **WHEN** handoff report generation does not receive external install evidence
- **THEN** the report SHALL mark customer-controlled host install evidence as `not_provided` or `operator_guided` rather than omitting the section

#### Scenario: External install evidence contains sensitive material
- **WHEN** external install evidence includes raw tokens, `.env` secrets, private source content, raw backup material, or unbounded customer logs
- **THEN** handoff report generation SHALL reject the evidence or preserve a `blocked` status without copying sensitive content into the report
