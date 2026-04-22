## ADDED Requirements

### Requirement: Repository lookup exposes imported workspace reuse state
The system SHALL let the product look up a repository before starting a live import so the UI can tell whether an imported workspace already exists within the current owner scope and whether incremental sync is available.

#### Scenario: Repository already has an imported workspace
- **WHEN** the user looks up a repository that already maps to an imported workspace in the current owner scope
- **THEN** the system SHALL return the workspace slug, latest import state, and whether incremental sync can be offered

#### Scenario: Repository has no existing imported workspace
- **WHEN** the user looks up a repository that has not been imported before in the current owner scope
- **THEN** the system SHALL report that no imported workspace exists yet and SHALL allow a new full analysis to start

#### Scenario: Same repository can exist in another scope without blocking reuse here
- **WHEN** the same repository already exists as an imported workspace in a different owner scope but not in the current one
- **THEN** the system SHALL still allow the current owner scope to create its own imported workspace

#### Scenario: Installation-backed workspace is identified during lookup
- **WHEN** the current owner scope already has an imported workspace bound through a GitHub App installation
- **THEN** repository lookup SHALL identify that workspace as installation-backed reusable state

#### Scenario: Private repository reuse requires authorized source in current scope
- **WHEN** the current owner scope looks up a private repository that has an existing imported workspace bound to an authorized source in that scope
- **THEN** repository lookup SHALL expose that workspace as reusable state

#### Scenario: Private repository from another scope is not reusable here
- **WHEN** a private repository has an imported workspace only in some other owner scope
- **THEN** repository lookup SHALL NOT expose that workspace as reusable state for the current actor

### Requirement: Imported workspaces expose latest sync provenance
The system SHALL expose latest sync provenance and bounded recent sync history for imported workspaces so product surfaces can explain whether a workspace is current, syncing, or behind.

#### Scenario: Latest sync provenance is available
- **WHEN** an imported workspace has completed at least one sync
- **THEN** the system SHALL expose the latest successful sync origin and timestamp in the workspace summary

#### Scenario: Recent sync history includes webhook-triggered runs
- **WHEN** an imported workspace has recent sync attempts from manual and webhook-triggered paths
- **THEN** the system SHALL expose enough bounded history for the product to distinguish those sync origins

### Requirement: Existing imported workspaces expose explicit next actions
The system SHALL let the product offer open-existing, incremental-sync, and full-rerun actions explicitly within the current owner scope instead of treating all repeat analysis requests as identical.

#### Scenario: Existing workspace can sync incrementally
- **WHEN** a repository has a successful prior import in the current owner scope and no active queued or running job
- **THEN** the system SHALL allow a `since_last_sync` import to be started for that workspace

#### Scenario: Existing workspace already has an active import
- **WHEN** the repository's latest import job is queued or running in the current owner scope
- **THEN** the system SHALL report that active state so the UI can discourage starting another duplicate run

#### Scenario: Incremental sync permission is owner-scoped
- **WHEN** a user attempts to trigger incremental sync for an imported workspace
- **THEN** the future platform model SHALL resolve whether that action is allowed within the workspace's owner scope before starting the sync

#### Scenario: Webhook-triggered sync and manual sync share the same workspace action surface
- **WHEN** the product loads an installation-backed imported workspace
- **THEN** it SHALL be able to describe both automatic webhook sync state and manual rerun/incremental actions without treating them as separate workspace types

#### Scenario: Private workspace keeps bound access source during sync
- **WHEN** an imported private-repository workspace was originally created through a bound owner-scoped access source
- **THEN** later incremental sync or rerun SHALL continue using that bound source unless the workspace is explicitly re-bound

#### Scenario: Viewer role cannot trigger rerun or sync
- **WHEN** an actor with only viewer role accesses an imported workspace
- **THEN** the product SHALL expose workspace state but SHALL deny rerun and incremental-sync actions

#### Scenario: System-triggered sync remains allowed without viewer/admin session
- **WHEN** a webhook or background execution path triggers incremental sync for a bound workspace
- **THEN** the platform SHALL continue that sync without requiring a user-facing viewer, reviewer, or admin browser session

### Requirement: Incremental sync uses normalized timestamps
The system SHALL normalize `since_last_sync` timestamps before comparing them against GitHub timestamps so incremental import filtering does not fail on naive-versus-aware datetime mismatches.

#### Scenario: Last successful import timestamp is naive
- **WHEN** the latest successful import timestamp has no timezone information
- **THEN** the system SHALL normalize it before comparing it with GitHub API timestamps

#### Scenario: Incremental sync filters updated pull requests safely
- **WHEN** the importer runs with `since_last_sync`
- **THEN** GitHub pull request filtering SHALL compare timestamps without raising naive-versus-aware datetime exceptions
