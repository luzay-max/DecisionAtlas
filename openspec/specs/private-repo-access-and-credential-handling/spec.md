## ADDED Requirements

### Requirement: Owner-scoped access sources can authorize private repository import
The system SHALL require private repository import to resolve through an owner-scoped authorized access source instead of assuming anonymous global access.

#### Scenario: Authorized source allows private repository import
- **WHEN** the current owner scope has an authorized access source that can reach a target private repository
- **THEN** the platform SHALL allow import of that repository within the current owner scope

#### Scenario: Missing source blocks private repository import
- **WHEN** the current owner scope has no authorized access source for a target private repository
- **THEN** the platform SHALL block import and report that private-repository access setup is required

### Requirement: Credential-bearing access sources are referenced separately from workspaces
The system SHALL store private-repository access through reusable owner-scoped access-source records and SHALL bind workspaces to those records without storing raw credential material on the workspace.

#### Scenario: Workspace binds to access-source reference
- **WHEN** a private repository import succeeds
- **THEN** the resulting workspace SHALL record which owner-scoped access source it is bound to

#### Scenario: Credential rotation does not redefine workspace identity
- **WHEN** the credential material behind an access source is rotated or refreshed
- **THEN** the platform SHALL preserve workspace identity while updating the bound source state

### Requirement: Private repository failures are reported as authorization outcomes
The system SHALL distinguish private-repository authorization failures from generic repository-not-found or network failures.

#### Scenario: Unauthorized source yields explicit failure class
- **WHEN** the current owner scope attempts to import a private repository through an invalid or unauthorized source
- **THEN** the platform SHALL report an authorization-specific failure outcome rather than collapsing it into a generic repository failure

#### Scenario: Credential-required outcome is exposed before blind import
- **WHEN** live analysis targets a private repository with no authorized source in the current owner scope
- **THEN** the platform SHALL return a credential-required outcome before starting a blind import job
