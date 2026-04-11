## MODIFIED Requirements

### Requirement: Repository access source is modeled separately from repository identity
The system SHALL distinguish repository identity from the access source used to reach it, so future private-repository and GitHub App behavior can be defined without conflating content identity with credential storage.

#### Scenario: Public and installed access paths can target the same repository
- **WHEN** the same repository can be reached through anonymous public access or an installation-bound access source
- **THEN** the platform model SHALL treat the repository as the same content identity while keeping the access source distinct

#### Scenario: Private repository access depends on owner-authorized source
- **WHEN** a repository is private
- **THEN** the platform model SHALL require that access be mediated through an owner-authorized credential or installation source

#### Scenario: GitHub App installation is one access-source type
- **WHEN** the platform defines GitHub App installation support
- **THEN** it SHALL model installation-based repository access as an access-source variant rather than as a separate workspace-ownership model

#### Scenario: Installation binding remains owner-scoped
- **WHEN** a GitHub App installation is linked to imported workspace behavior
- **THEN** the platform model SHALL define that installation binding in terms of the owner scope that controls the access source rather than as a global repository property

### Requirement: Platform permissions are defined as product actions
The system SHALL define platform permissions in terms of product actions such as import, reuse, sync, review, accept, and drift evaluation.

#### Scenario: Reviewer permission can be described without route details
- **WHEN** the platform model defines who can review candidate decisions
- **THEN** it SHALL express that in terms of the review action on a workspace rather than raw route-level implementation details

#### Scenario: Sync permission can be distinguished from view permission
- **WHEN** the platform model defines who can view a workspace and who can trigger rerun or incremental sync
- **THEN** it SHALL represent those as distinct actions that can be granted differently

#### Scenario: Credential management is more privileged than review
- **WHEN** the platform model defines who may manage repository access sources
- **THEN** it SHALL distinguish that action from ordinary reviewer actions such as screening or drift evaluation

#### Scenario: Webhook-triggered sync follows an owner-scoped action boundary
- **WHEN** the platform defines webhook-triggered incremental sync
- **THEN** it SHALL treat that sync as an owner-scoped product action whose authority derives from the bound access source rather than from an anonymous global trigger
