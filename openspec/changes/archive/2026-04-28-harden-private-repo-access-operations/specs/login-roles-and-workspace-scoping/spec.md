## ADDED Requirements

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
