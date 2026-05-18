# platform-foundation Specification

## Purpose
Define the platform-level ownership, access-source, and product-action permission model that imported workspaces, GitHub App access, private repository access, and role-gated product surfaces build on.
## Requirements
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

#### Scenario: Token-backed private access is also an access-source variant
- **WHEN** the platform defines private repository access through token-backed credentials
- **THEN** it SHALL model that credential path as another owner-scoped access-source variant rather than as a special workspace type

### Requirement: Platform permissions are defined as product actions
The system SHALL define platform permissions in terms of product actions such as import, reuse, sync, review, accept, drift evaluation, and GitHub App installation binding, and SHALL expose enough current-session role context for the product to present those actions safely.

#### Scenario: Reviewer permission can be described without route details
- **WHEN** the platform model defines who can review candidate decisions
- **THEN** it SHALL express that in terms of the review action on a workspace rather than raw route-level implementation details

#### Scenario: Sync permission can be distinguished from view permission
- **WHEN** the platform model defines who can view a workspace and who can trigger rerun or incremental sync
- **THEN** it SHALL represent those as distinct actions that can be granted differently

#### Scenario: Credential management is more privileged than review
- **WHEN** the platform model defines who may manage repository access sources
- **THEN** it SHALL distinguish that action from ordinary reviewer actions such as screening or drift evaluation

#### Scenario: GitHub App installation binding is admin-only
- **WHEN** the platform model defines who may bind a repository to a GitHub App installation access source
- **THEN** it SHALL treat that binding as an admin-level owner-scoped product action

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

### Requirement: v0.3 platform baseline distinguishes productized flows from full SaaS
The system SHALL describe the v0.3 platform baseline as productized owner-scoped access and workspace lifecycle flows while keeping full SaaS administration outside the release-candidate scope.

#### Scenario: Productized flows are included in the baseline
- **WHEN** the v0.3 release candidate describes platform capabilities
- **THEN** it SHALL include authenticated session recovery, owner-scope switching, role-gated product actions, GitHub App installation binding, and token-backed private repository access binding

#### Scenario: Full SaaS capabilities remain out of scope
- **WHEN** the v0.3 release candidate describes platform limitations
- **THEN** it SHALL state that billing, org administration, secret vault, GitHub Marketplace/OAuth self-service installation, and collaborative review workflows are not included

#### Scenario: Follow-up work starts from the RC baseline
- **WHEN** later platform hardening changes are proposed
- **THEN** they SHALL identify whether they harden the v0.3 RC baseline or introduce capabilities beyond that baseline

### Requirement: Platform baseline supports self-hosted commercial packaging
The platform baseline SHALL distinguish near-term self-hosted commercial packaging from full hosted SaaS platform capabilities.

#### Scenario: Self-hosted packaging is described
- **WHEN** product or platform documentation describes the near-term commercial baseline
- **THEN** it SHALL describe Community, Team Self-hosted, and Enterprise Self-hosted as the current packaging direction
- **AND** it SHALL tie those tiers to local/private deployment, owner-scoped workspace behavior, evidence generation, and support boundaries.

#### Scenario: Hosted SaaS remains optional future scope
- **WHEN** platform documentation discusses billing, hosted multi-tenancy, full SaaS organization administration, Marketplace or self-service OAuth installation, or hosted secret custody
- **THEN** it SHALL identify those capabilities as future optional hosted managed service work rather than prerequisites for the self-hosted baseline.

