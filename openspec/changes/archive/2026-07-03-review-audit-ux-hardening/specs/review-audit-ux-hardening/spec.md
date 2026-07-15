## ADDED Requirements

### Requirement: Review UI exposes role and next action context
The review UI SHALL clearly show the current role and available next actions.

#### Scenario: Reviewer opens review queue
- **WHEN** a reviewer opens the review page
- **THEN** the UI SHALL show that review actions are available and explain the next review step.

#### Scenario: Viewer opens review queue
- **WHEN** a viewer opens the review page
- **THEN** the UI SHALL show a read-only explanation and SHALL NOT present enabled review action controls.

### Requirement: Review audit trail is visible
The review UI SHALL expose recent review/audit activity near the review workflow.

#### Scenario: Audit records exist
- **WHEN** recent review or audit records exist
- **THEN** the UI SHALL show actor, action, target decision, and timestamp or bounded source context.

#### Scenario: No audit records exist
- **WHEN** no review/audit records exist
- **THEN** the UI SHALL show an empty state with the next action to create review evidence.

### Requirement: Review interaction remains browser-verifiable
Review/audit hardening SHALL be covered by automated tests.

#### Scenario: Browser rehearsal runs
- **WHEN** the review audit UX browser test runs
- **THEN** it SHALL verify role guidance, read-only viewer behavior, and audit trail visibility.
