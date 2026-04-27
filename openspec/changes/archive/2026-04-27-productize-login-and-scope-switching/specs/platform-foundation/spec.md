## MODIFIED Requirements

### Requirement: Workspace ownership is explicit
The system SHALL define imported workspaces as belonging to an explicit owner scope rather than treating repository workspaces as globally shared objects, and SHALL make the current owner scope visible in product navigation before users perform workspace actions.

#### Scenario: Same repository may exist in different owner scopes
- **WHEN** two different owner scopes import the same repository
- **THEN** the platform model SHALL allow those imports to resolve to separate workspace identities instead of assuming one global workspace mapping

#### Scenario: Workspace visibility is derived from owner scope
- **WHEN** a user accesses an imported workspace
- **THEN** the platform model SHALL define that workspace visibility in terms of the owner scope that owns it

#### Scenario: Existing globally scoped workspaces can be backfilled
- **WHEN** the platform migrates from the current global imported-workspace model
- **THEN** it SHALL define a migration path that can assign existing workspaces into a default owner scope without breaking the current single-user baseline

#### Scenario: Product navigation exposes current owner scope
- **WHEN** a user navigates imported workspace surfaces
- **THEN** the product SHALL expose the current owner scope so workspace identity is not interpreted as globally shared

### Requirement: Platform permissions are defined as product actions
The system SHALL define platform permissions in terms of product actions such as import, reuse, sync, review, accept, and drift evaluation, and SHALL expose enough current-session role context for the product to present those actions safely.

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

#### Scenario: Private credential setup remains more privileged than import review
- **WHEN** the platform defines who may register, rotate, or revoke private repository access sources
- **THEN** it SHALL treat those actions as more privileged than candidate review, acceptance, or drift evaluation

#### Scenario: Product actions are enforced through authenticated scope membership
- **WHEN** an actor attempts to perform a platform product action
- **THEN** the system SHALL evaluate that action against the actor's role within the current owner scope rather than against a global unauthenticated baseline

#### Scenario: Trusted system actions are enforced through bound authority
- **WHEN** the platform executes a webhook-triggered sync or background job action
- **THEN** it SHALL authorize that action through bound workspace/access-source state rather than through an interactive actor session

#### Scenario: Product action controls reflect current role
- **WHEN** the product renders workspace lifecycle actions
- **THEN** it SHALL use the current session role and owner scope to distinguish available, disabled, and hidden actions
