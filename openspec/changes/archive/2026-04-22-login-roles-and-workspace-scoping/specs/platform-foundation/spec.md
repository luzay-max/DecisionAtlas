## MODIFIED Requirements

### Requirement: Platform permissions are defined as product actions
The system SHALL define platform permissions in terms of product actions such as import, reuse, sync, review, accept, and drift evaluation, and SHALL bind those permissions to authenticated actor roles within an owner scope rather than to anonymous callers.

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
