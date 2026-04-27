## MODIFIED Requirements

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
