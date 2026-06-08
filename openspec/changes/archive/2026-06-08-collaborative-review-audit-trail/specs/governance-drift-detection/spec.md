## ADDED Requirements

### Requirement: Drift alerts can be manually dispositioned with audit history
The drift experience SHALL allow authorized reviewers to record bounded manual drift alert disposition and preserve the action as audit history.

#### Scenario: Reviewer resolves drift alert
- **WHEN** a reviewer marks a drift alert as acknowledged, resolved, or false positive with rationale
- **THEN** the system SHALL update the alert disposition state and persist an audit event with actor, role, previous status, new status, rationale, and timestamp

#### Scenario: Viewer sees drift handling history
- **WHEN** a viewer opens a drift alert detail that has disposition history
- **THEN** the product SHALL show who handled the alert, what status changed, when it changed, and the rationale when present

#### Scenario: Invalid drift disposition is rejected
- **WHEN** a user submits an unsupported drift alert disposition state or lacks reviewer permission
- **THEN** the system SHALL reject the action with a bounded error and SHALL NOT create an audit event
