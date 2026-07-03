## ADDED Requirements

### Requirement: Role affordances are visible in review workflows
Workspace member permission state SHALL be visible in review workflows.

#### Scenario: Admin or reviewer has action permission
- **WHEN** the current role can review decisions
- **THEN** review controls SHALL be presented as available actions.

#### Scenario: Viewer lacks review permission
- **WHEN** the current role is viewer
- **THEN** review controls SHALL be disabled or absent and the UI SHALL explain the read-only boundary.
