## ADDED Requirements

### Requirement: Product actions require an authenticated actor
The system SHALL resolve an authenticated actor before allowing imported-workspace product actions that read or mutate owner-scoped state, except for trusted system-triggered actions whose authority derives from bound platform state rather than an interactive session.

#### Scenario: Anonymous actor cannot access imported workspace actions
- **WHEN** a request targets imported-workspace dashboard, search, review, sync, or drift actions without an authenticated actor
- **THEN** the system SHALL reject the request instead of treating it as an anonymous global session

#### Scenario: Authenticated actor can establish product session
- **WHEN** a user successfully authenticates through the supported login path
- **THEN** the system SHALL establish an application session that identifies that actor for subsequent requests

#### Scenario: System-triggered sync does not require browser session
- **WHEN** a webhook-triggered or background sync action executes through a trusted internal path
- **THEN** the system SHALL allow that action to proceed without requiring an interactive browser login session

### Requirement: Owner-scope membership defines role assignments
The system SHALL assign product roles through owner-scope membership rather than through global user roles.

#### Scenario: Same actor can hold different roles in different scopes
- **WHEN** the same actor belongs to multiple owner scopes
- **THEN** the system SHALL allow that actor to hold different product roles in those different scopes

#### Scenario: Actor without membership cannot act inside scope
- **WHEN** an authenticated actor targets an owner scope where they have no membership
- **THEN** the system SHALL deny visibility and actions for workspaces in that scope

#### Scenario: Session carries current owner scope
- **WHEN** an authenticated actor has access to one or more owner scopes
- **THEN** the product SHALL resolve one current owner scope from session state before evaluating workspace visibility or actions

### Requirement: Product roles map to workspace lifecycle actions
The system SHALL enforce viewer, reviewer, and admin permissions against imported-workspace lifecycle actions.

#### Scenario: Reviewer can review but cannot manage imports
- **WHEN** an actor has reviewer role in the current owner scope
- **THEN** the system SHALL allow candidate review, decision acceptance, and drift evaluation while denying import, rerun, and credential-management actions

#### Scenario: Admin can manage repository-backed lifecycle actions
- **WHEN** an actor has admin role in the current owner scope
- **THEN** the system SHALL allow import, rerun, incremental sync, access-source management, and member-management actions in that scope

### Requirement: Bootstrap local mode preserves the current single-user baseline
The system SHALL provide a bootstrap local actor and owner-scope path so the current single-user local product flow continues to work while auth and scope enforcement are introduced.

#### Scenario: Existing local workspace data is backfilled into bootstrap scope
- **WHEN** the platform migrates an existing single-user local installation
- **THEN** it SHALL backfill current imported-workspace data into a bootstrap owner scope and admin membership without breaking existing workspaces

#### Scenario: Local developer flow still works after auth lands
- **WHEN** the platform is running in the current local developer baseline
- **THEN** a bootstrap admin path SHALL allow the existing import, review, why, and drift flows to remain usable
