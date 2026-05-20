## ADDED Requirements

### Requirement: Workspace visibility is membership-bounded
The system SHALL restrict workspace visibility to users with owner-scope or workspace membership.

#### Scenario: Member lists authorized workspaces
- **WHEN** a user requests workspace lists or workspace navigation
- **THEN** the system SHALL return only workspaces visible to that user's current scope and membership.

#### Scenario: Non-member opens workspace
- **WHEN** an authenticated user opens a workspace where they have no membership and no owner-scope fallback permission
- **THEN** the system SHALL deny access
- **AND** it SHALL NOT reveal private access-source details for that workspace.

### Requirement: Workspace roles control product actions
The system SHALL enforce admin, reviewer, and viewer permissions for workspace actions.

#### Scenario: Viewer reads workspace evidence
- **WHEN** a viewer opens an authorized workspace
- **THEN** the system SHALL allow read-only dashboard, decision detail, why-search, drift status, timeline, and evidence views.

#### Scenario: Viewer attempts mutation
- **WHEN** a viewer attempts import, sync, review, drift evaluation, governance mutation, private access setup, or account management
- **THEN** the system SHALL reject the action.

#### Scenario: Reviewer performs review action
- **WHEN** a reviewer reviews candidate decisions or handles drift in an authorized workspace
- **THEN** the system SHALL allow the review action
- **AND** it SHALL deny repository import, private credential setup, account management, and workspace member management.

#### Scenario: Admin manages workspace
- **WHEN** an admin manages an authorized workspace
- **THEN** the system SHALL allow import, rerun, sync, private access setup, member assignment, and governance administration for that workspace.

### Requirement: Workspace membership can be administered
The product SHALL let admins manage which users can access each workspace.

#### Scenario: Admin grants workspace membership
- **WHEN** an admin adds a user to a workspace with viewer, reviewer, or admin role
- **THEN** that user SHALL gain the corresponding visibility and actions for that workspace.

#### Scenario: Admin removes workspace membership
- **WHEN** an admin removes a user from a workspace
- **THEN** that user SHALL lose access to the workspace unless owner-scope fallback still grants access.

### Requirement: Permission boundaries are product-readable
The product SHALL show permission boundaries clearly rather than presenting authorization failures as missing data.

#### Scenario: User lacks action permission
- **WHEN** an action is unavailable because the user's role is insufficient
- **THEN** the product SHALL show a permission explanation
- **AND** it SHALL NOT imply that the workspace or decision data is missing.
