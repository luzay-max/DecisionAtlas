## ADDED Requirements

### Requirement: Product exposes private repository access setup
The system SHALL provide an admin-facing product surface for binding token-backed private repository access to a repository inside the current owner scope.

#### Scenario: Admin opens private access setup
- **WHEN** an admin views the live analysis or workspace management surface
- **THEN** the product SHALL expose a private repository access setup entry point for the current owner scope

#### Scenario: Reviewer cannot manage private access setup
- **WHEN** a reviewer or viewer views the same product surface
- **THEN** the product SHALL hide or disable private access setup controls and explain that admin role is required

#### Scenario: Current owner scope is visible during setup
- **WHEN** the private access setup surface is shown
- **THEN** the product SHALL display the current owner scope so the admin knows where the access source will be bound

### Requirement: Admin can bind repository to token-backed access source
The system SHALL let an admin bind a repository to a reusable token-backed GitHub access source by using the existing private-access binding API.

#### Scenario: Private access binding succeeds
- **WHEN** an admin submits a repository and GitHub token for the current owner scope
- **THEN** the product SHALL call the private-access binding API and show the resulting access-source label, authorization status, and workspace slug

#### Scenario: Private access binding fails validation
- **WHEN** the private-access binding API rejects the repository or token payload
- **THEN** the product SHALL show a bounded error message without changing the visible workspace state

#### Scenario: Binding keeps session scope as authority
- **WHEN** the product submits private-access binding
- **THEN** it SHALL rely on the current authenticated session scope rather than allowing a typed owner-scope override

#### Scenario: Credential material is not echoed after submit
- **WHEN** private-access binding succeeds or fails
- **THEN** the product SHALL NOT render the submitted token back to the user

### Requirement: Token-backed workspace state is visible
The system SHALL identify token-backed private workspace state in live analysis and workspace surfaces using access-source and authorization metadata.

#### Scenario: Lookup finds token-backed workspace
- **WHEN** repository lookup finds an imported workspace bound through a token-backed private access source
- **THEN** the product SHALL show that private access-source label and status before offering open, sync, or rerun actions

#### Scenario: Workspace dashboard shows token-backed source
- **WHEN** a token-backed private workspace dashboard is shown
- **THEN** the product SHALL display the private access-source label, authorization status, and authorization detail when available
