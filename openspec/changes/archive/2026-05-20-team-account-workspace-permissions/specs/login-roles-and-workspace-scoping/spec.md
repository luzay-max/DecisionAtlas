## ADDED Requirements

### Requirement: Team-created users participate in product sessions
The system SHALL allow administrator-created team users to authenticate through the existing product login and session recovery path.

#### Scenario: Team user logs in
- **WHEN** an enabled team user submits valid credentials through the login page
- **THEN** the system SHALL establish a product session
- **AND** it SHALL return actor identity, current owner scope, role, and available authorized workspaces or scopes.

#### Scenario: Disabled team user cannot use session
- **WHEN** a disabled team user attempts login or session recovery
- **THEN** the system SHALL reject the request
- **AND** it SHALL NOT allow workspace actions with any previously issued session token.

### Requirement: Session role reflects effective workspace permission
The system SHALL expose enough session and workspace authorization data for the product to render safe role-gated actions.

#### Scenario: User has different permissions by workspace
- **WHEN** a user has different roles across workspaces
- **THEN** the product SHALL evaluate action availability using the effective role for the current workspace rather than assuming one global role.

#### Scenario: Workspace role is unavailable
- **WHEN** the product cannot resolve an effective workspace role for the current user
- **THEN** it SHALL treat mutating actions as unavailable until authorization is resolved.

### Requirement: Local bootstrap mode remains compatible with team accounts
The system SHALL preserve local bootstrap auth while supporting administrator-created team users.

#### Scenario: Bootstrap mode is enabled
- **WHEN** local bootstrap auth is enabled and no browser session exists
- **THEN** the system SHALL recover or create the bootstrap admin session as before
- **AND** it SHALL make clear that this is a bootstrap admin identity.

#### Scenario: Real team admin exists
- **WHEN** a non-bootstrap admin account exists
- **THEN** the system SHALL still allow normal username/password login for that account
- **AND** it SHALL NOT require SaaS signup or external identity provider configuration.
