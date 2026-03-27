## ADDED Requirements

### Requirement: Repository lookup exposes imported workspace reuse state
The system SHALL let the product look up a repository before starting a live import so the UI can tell whether an imported workspace already exists and whether incremental sync is available.

#### Scenario: Repository already has an imported workspace
- **WHEN** the user looks up a repository that already maps to an imported workspace
- **THEN** the system SHALL return the workspace slug, latest import state, and whether incremental sync can be offered

#### Scenario: Repository has no existing imported workspace
- **WHEN** the user looks up a repository that has not been imported before
- **THEN** the system SHALL report that no imported workspace exists yet and SHALL allow a new full analysis to start

### Requirement: Existing imported workspaces expose explicit next actions
The system SHALL let the product offer open-existing, incremental-sync, and full-rerun actions explicitly instead of treating all repeat analysis requests as identical.

#### Scenario: Existing workspace can sync incrementally
- **WHEN** a repository has a successful prior import and no active queued or running job
- **THEN** the system SHALL allow a `since_last_sync` import to be started for the existing workspace

#### Scenario: Existing workspace already has an active import
- **WHEN** the repository's latest import job is queued or running
- **THEN** the system SHALL report that active state so the UI can discourage starting another duplicate run

### Requirement: Incremental sync uses normalized timestamps
The system SHALL normalize `since_last_sync` timestamps before comparing them against GitHub timestamps so incremental import filtering does not fail on naive-versus-aware datetime mismatches.

#### Scenario: Last successful import timestamp is naive
- **WHEN** the latest successful import timestamp has no timezone information
- **THEN** the system SHALL normalize it before comparing it with GitHub API timestamps

#### Scenario: Incremental sync filters updated pull requests safely
- **WHEN** the importer runs with `since_last_sync`
- **THEN** GitHub pull request filtering SHALL compare timestamps without raising naive-versus-aware datetime exceptions
