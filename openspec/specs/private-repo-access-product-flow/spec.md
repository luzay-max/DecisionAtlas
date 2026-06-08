## Purpose
Define the product flow for configuring and using private repository access.
## Requirements
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

### Requirement: Private access product surfaces show actionable source state
The product SHALL show token-backed private repository access-source state consistently before users choose open, sync, rerun, or troubleshooting actions.

#### Scenario: Lookup shows token-backed state before actions
- **WHEN** repository lookup finds a token-backed private workspace in the current owner scope
- **THEN** the product SHALL show access-source label, authorization status, and bounded authorization detail before open, sync, or rerun actions

#### Scenario: Dashboard shows token-backed operational state
- **WHEN** a token-backed private workspace dashboard is rendered
- **THEN** the product SHALL show the private access-source label, authorization status, and safe detail when available

#### Scenario: Private access setup explains recovery
- **WHEN** private access binding fails because credentials are missing, unauthorized, invalid, or cannot reach the repository
- **THEN** the product SHALL display a bounded recovery-oriented message without rendering the submitted token

### Requirement: Private access setup documents current security boundary
The product and operator documentation SHALL explain the current token-backed private access boundary.

#### Scenario: Admin sees token handling boundary
- **WHEN** an admin opens private access setup
- **THEN** the product or linked documentation SHALL explain that tokens are used to create an owner-scoped access source and are not echoed back after submission

#### Scenario: Operator sees supported token guidance
- **WHEN** hosted-preview documentation describes private repository access
- **THEN** it SHALL include recommended minimum permissions, rotation guidance, troubleshooting steps, and explicit non-goals such as no secret vault or OAuth self-service

### Requirement: Private access setup becomes provider-aware
The admin private access setup surface SHALL allow repository access setup to be expressed in provider-aware terms while preserving the existing GitHub token-backed behavior.

#### Scenario: Admin sees provider and access mode
- **WHEN** an admin opens repository access setup
- **THEN** the product SHALL show provider and access-mode fields or labels so the admin understands whether they are configuring public, token, or local-path access

#### Scenario: GitHub token setup still works
- **WHEN** an admin submits a GitHub token-backed setup request
- **THEN** the product SHALL use the existing GitHub private-access binding behavior and show safe provider/access status

#### Scenario: Non-admin cannot manage provider setup
- **WHEN** a reviewer or viewer opens the same surface
- **THEN** the product SHALL hide or disable provider/token/local-path setup controls and explain that admin role is required
