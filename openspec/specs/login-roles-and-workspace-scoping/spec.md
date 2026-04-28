## Purpose
Define authentication, role, and workspace-scope requirements for product actions.
## Requirements
### Requirement: Product actions require an authenticated actor
The system SHALL resolve an authenticated actor before allowing imported-workspace product actions that read or mutate owner-scoped state, SHALL expose a product login and session-recovery path for browser users, and SHALL preserve trusted system-triggered actions whose authority derives from bound platform state rather than an interactive session.

#### Scenario: Anonymous actor cannot access imported workspace actions
- **WHEN** a request targets imported-workspace dashboard, search, review, sync, or drift actions without an authenticated actor
- **THEN** the system SHALL reject the request instead of treating it as an anonymous global session

#### Scenario: Authenticated actor can establish product session
- **WHEN** a user successfully authenticates through the supported login path
- **THEN** the system SHALL establish an application session that identifies that actor for subsequent requests

#### Scenario: Product can recover existing browser session
- **WHEN** a browser returns with a valid existing application session
- **THEN** the product SHALL recover the actor, current owner scope, role, and available scopes without requiring a new login

#### Scenario: Product shows login-required state
- **WHEN** a browser has no valid session and local bootstrap auth is not available
- **THEN** the product SHALL show an explicit login-required state before allowing imported-workspace actions

#### Scenario: System-triggered sync does not require browser session
- **WHEN** a webhook-triggered or background sync action executes through a trusted internal path
- **THEN** the system SHALL allow that action to proceed without requiring an interactive browser login session

### Requirement: Owner-scope membership defines role assignments
The system SHALL assign product roles through owner-scope membership rather than through global user roles, and SHALL expose the actor's available owner scopes so the product can switch current scope safely.

#### Scenario: Same actor can hold different roles in different scopes
- **WHEN** the same actor belongs to multiple owner scopes
- **THEN** the system SHALL allow that actor to hold different product roles in those different scopes

#### Scenario: Actor without membership cannot act inside scope
- **WHEN** an authenticated actor targets an owner scope where they have no membership
- **THEN** the system SHALL deny visibility and actions for workspaces in that scope

#### Scenario: Session carries current owner scope
- **WHEN** an authenticated actor has access to one or more owner scopes
- **THEN** the product SHALL resolve one current owner scope from session state before evaluating workspace visibility or actions

#### Scenario: Session exposes available owner scopes
- **WHEN** the product reads the current session
- **THEN** the system SHALL return the actor's available owner scopes and role per scope so the product can render a safe scope switcher

### Requirement: Product roles map to workspace lifecycle actions
The system SHALL enforce viewer, reviewer, and admin permissions against imported-workspace lifecycle actions and SHALL let the product present action availability according to the actor's role in the current owner scope, including private repository access setup as an admin-only access-source management action.

#### Scenario: Reviewer can review but cannot manage imports
- **WHEN** an actor has reviewer role in the current owner scope
- **THEN** the system SHALL allow candidate review, decision acceptance, and drift evaluation while denying import, rerun, and credential-management actions

#### Scenario: Admin can manage repository-backed lifecycle actions
- **WHEN** an actor has admin role in the current owner scope
- **THEN** the system SHALL allow import, rerun, incremental sync, access-source management, private repository access setup, and member-management actions in that scope

#### Scenario: Product distinguishes disabled actions from missing data
- **WHEN** a workspace action is unavailable because the actor's current-scope role is insufficient
- **THEN** the product SHALL present that as a permission boundary rather than as missing workspace data

#### Scenario: Non-admin cannot submit private access credentials
- **WHEN** an actor without admin role views private repository access setup
- **THEN** the product SHALL prevent credential submission and explain that admin role in the current owner scope is required

### Requirement: Bootstrap local mode preserves the current single-user baseline
The system SHALL provide a bootstrap local actor and owner-scope path so the current single-user local product flow continues to work while auth and scope enforcement are introduced, and SHALL make that bootstrap identity visible in the product session surface.

#### Scenario: Existing local workspace data is backfilled into bootstrap scope
- **WHEN** the platform migrates an existing single-user local installation
- **THEN** it SHALL backfill current imported-workspace data into a bootstrap owner scope and admin membership without breaking existing workspaces

#### Scenario: Local developer flow still works after auth lands
- **WHEN** the platform is running in the current local developer baseline
- **THEN** a bootstrap admin path SHALL allow the existing import, review, why, and drift flows to remain usable

#### Scenario: Bootstrap session is visible to local users
- **WHEN** local bootstrap auth automatically creates a session
- **THEN** the product SHALL display that the current session is the local bootstrap admin session

### Requirement: Private access operations remain admin-only and session-scoped
The system SHALL keep private repository credential setup constrained to admins in the current owner scope.

#### Scenario: Non-admin cannot submit private token
- **WHEN** an actor without admin role attempts to submit token-backed private repository access
- **THEN** the system SHALL deny the action and SHALL NOT create or update an access source

#### Scenario: Product does not accept typed owner override
- **WHEN** an admin submits token-backed private repository access setup
- **THEN** the system SHALL derive owner scope from the authenticated session rather than accepting a user-typed owner-scope override

#### Scenario: Cross-scope private source is not leaked
- **WHEN** a repository has a token-backed access source in another owner scope
- **THEN** lookup and setup results for the current actor SHALL NOT expose that other scope's credential source or workspace state

