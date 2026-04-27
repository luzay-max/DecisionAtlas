## ADDED Requirements

### Requirement: Product shell exposes authenticated session state
The system SHALL expose the current authenticated actor, role, and owner scope in the product shell so users can tell which platform boundary they are operating in.

#### Scenario: Authenticated session appears in navigation
- **WHEN** a user has an active product session
- **THEN** the web product SHALL display the current actor identity, current owner scope, and role in a persistent navigation or account surface

#### Scenario: Unauthenticated product session prompts login
- **WHEN** a hosted or non-bootstrap environment cannot recover an authenticated session
- **THEN** the web product SHALL show a login path instead of presenting imported workspace actions as anonymous global actions

#### Scenario: Local bootstrap session remains visible
- **WHEN** local bootstrap auth creates a session automatically
- **THEN** the web product SHALL identify the user as the local bootstrap actor and show the bootstrap owner scope rather than hiding the session boundary

### Requirement: Product shell supports owner-scope switching
The system SHALL allow an authenticated actor with multiple owner-scope memberships to switch the current owner scope from the product UI, and SHALL refresh scoped product state after the switch.

#### Scenario: User switches to an available owner scope
- **WHEN** an authenticated actor selects another owner scope from the available scopes list
- **THEN** the product SHALL call the scope-switching API, update the visible current scope, and refresh scope-bound data

#### Scenario: User cannot select unavailable owner scope
- **WHEN** an owner scope is not part of the authenticated actor's memberships
- **THEN** the product SHALL NOT present it as a selectable scope and SHALL surface any attempted switch failure as a permission boundary

#### Scenario: Scope switch preserves the current session
- **WHEN** scope switching succeeds
- **THEN** the product SHALL keep the same authenticated session while changing the current owner scope

### Requirement: Scoped workspace navigation is product-visible
The system SHALL make owner-scope boundaries visible when navigating to imported workspaces so users can understand whether a workspace is available in the current scope.

#### Scenario: Workspace unavailable in current scope
- **WHEN** a user navigates to a workspace that does not belong to the current owner scope
- **THEN** the product SHALL show a scoped unavailable or not-found state rather than leaking workspace details from another scope

#### Scenario: Workspace actions reflect current scope role
- **WHEN** a user views an imported workspace in the current owner scope
- **THEN** the product SHALL present workspace actions according to the user's role in that scope

#### Scenario: Same repository can be explained across scopes
- **WHEN** the same repository has separate imported workspaces in different owner scopes
- **THEN** the product SHALL make the current owner scope visible enough that users can tell which workspace instance they are viewing
