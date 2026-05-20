## ADDED Requirements

### Requirement: Administrators can manage local team accounts
The system SHALL provide administrator-managed local accounts for self-hosted team deployments.

#### Scenario: Admin creates user account
- **WHEN** an admin submits a username, temporary password, display name, and role for a new team member
- **THEN** the system SHALL create a local account
- **AND** it SHALL assign the requested role within the current owner scope.

#### Scenario: Non-admin cannot create account
- **WHEN** a reviewer or viewer attempts to create a user account
- **THEN** the system SHALL reject the request
- **AND** it SHALL NOT create an account or membership.

### Requirement: Administrators can disable and recover accounts
The system SHALL let administrators disable accounts and reset passwords without deleting historical attribution.

#### Scenario: Admin disables account
- **WHEN** an admin disables a user account
- **THEN** the system SHALL prevent that account from establishing or using sessions
- **AND** prior review or governance history associated with that actor SHALL remain readable.

#### Scenario: Admin resets password
- **WHEN** an admin resets a user's password
- **THEN** the system SHALL update the stored password hash
- **AND** it SHALL NOT expose the previous password hash or current session token.

### Requirement: Account management is visible only to admins
The product SHALL expose account-management controls only to administrators in the current owner scope.

#### Scenario: Admin opens account management
- **WHEN** an admin views team settings
- **THEN** the product SHALL show user list, create account, disable account, password reset, and role assignment controls.

#### Scenario: Reviewer or viewer opens team settings
- **WHEN** a reviewer or viewer views team settings
- **THEN** the product SHALL hide or disable account-management controls
- **AND** it SHALL explain that admin role is required.

### Requirement: Bootstrap admin can initialize team accounts
The system SHALL allow the local bootstrap admin to create the first self-hosted team accounts while remaining visibly marked as bootstrap.

#### Scenario: Bootstrap admin creates first real admin
- **WHEN** a deployment is using local bootstrap auth
- **THEN** the bootstrap admin SHALL be able to create a non-bootstrap admin account for the current owner scope.

#### Scenario: Bootstrap session is identified
- **WHEN** account-management UI shows the current actor
- **THEN** it SHALL indicate when that actor is the local bootstrap admin.
