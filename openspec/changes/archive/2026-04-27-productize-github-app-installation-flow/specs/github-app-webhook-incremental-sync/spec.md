## MODIFIED Requirements

### Requirement: GitHub App installations can bind repositories to an owner scope
The system SHALL allow an owner scope to register a GitHub App installation as a repository access source, bind imported repositories to that installation-backed source without changing repository identity, and expose that binding through an admin-facing product flow.

#### Scenario: Installation-backed repository is bound to an owner scope
- **WHEN** an owner scope authorizes a GitHub App installation for a repository
- **THEN** the platform SHALL store that installation as an access source that can be linked to imported workspaces in that owner scope

#### Scenario: Same repository can be bound through different installations in different scopes
- **WHEN** two owner scopes authorize different GitHub App installations for the same repository
- **THEN** the platform SHALL allow each owner scope to bind its own imported workspace without collapsing them into a single shared installation-backed workspace

#### Scenario: Product binding creates installation-backed access source
- **WHEN** an admin binds a repository to a GitHub App installation from the product surface
- **THEN** the platform SHALL create or update the owner-scoped installation-backed access source and return the resulting workspace access-source state

### Requirement: GitHub webhooks can trigger incremental sync for installation-backed workspaces
The system SHALL resolve qualifying GitHub App webhook events into the correct owner-scoped imported workspace and enqueue incremental sync using the existing `since_last_sync` path.

#### Scenario: Qualifying webhook enqueues incremental sync
- **WHEN** a qualifying webhook event arrives for a repository that is bound to an imported workspace through an owner-scoped GitHub App installation
- **THEN** the platform SHALL enqueue incremental sync for that workspace instead of requiring a user to start a rerun manually

#### Scenario: Webhook for unresolved repository does not enqueue blind import
- **WHEN** a webhook event arrives but no installation-backed imported workspace can be resolved in the owning scope
- **THEN** the platform SHALL record an ignored-or-unresolved webhook outcome rather than creating a blind workspace import

#### Scenario: Active sync prevents duplicate webhook-triggered enqueue
- **WHEN** a qualifying webhook event arrives while the target workspace already has an active queued or running sync
- **THEN** the platform SHALL avoid enqueuing a duplicate sync for the same workspace

### Requirement: Installation-backed workspaces expose sync provenance
The system SHALL expose whether the latest workspace update came from manual rerun, manual incremental sync, or webhook-triggered incremental sync so product surfaces can explain current workspace freshness.

#### Scenario: Workspace summary shows latest sync origin
- **WHEN** an imported workspace has completed at least one sync
- **THEN** the platform SHALL expose the latest successful sync origin and timestamp in a reusable summary form

#### Scenario: Workspace summary shows active webhook-triggered sync
- **WHEN** an imported workspace is currently processing a webhook-triggered incremental sync
- **THEN** the platform SHALL expose that active sync state distinctly enough for product surfaces to describe it

#### Scenario: Product shows installation-backed sync source
- **WHEN** the product renders an installation-backed workspace with sync provenance
- **THEN** it SHALL describe the source as GitHub App-backed rather than as anonymous public access
