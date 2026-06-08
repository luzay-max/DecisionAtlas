## ADDED Requirements

### Requirement: Decision review history is visible
The decision review experience SHALL expose bounded review history for imported and demo decisions without changing the existing accept, reject, supersede, and candidate actions.

#### Scenario: Decision detail shows review history
- **WHEN** a viewer opens a decision that has review audit events
- **THEN** the detail view SHALL show the recent review history including actor, action, previous review state, new review state, rationale when present, and timestamp

#### Scenario: Review action response includes audit event
- **WHEN** a reviewer changes a decision review state
- **THEN** the review response SHALL include or make available the resulting audit event so product surfaces can update without a page reload

#### Scenario: Review queue remains simple
- **WHEN** a reviewer evaluates imported candidate decisions from the review queue
- **THEN** the product SHALL preserve the existing simple candidate action flow while making recent review history available on the detail page or compact card context
