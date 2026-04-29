## ADDED Requirements

### Requirement: Live analysis entry presents reuse choices before repeat import
The live-analysis entry flow SHALL present existing workspace reuse choices before starting another import when repository lookup finds a workspace in the current owner scope.

#### Scenario: Form submit finds existing workspace
- **WHEN** the user enters a repository that already maps to an imported workspace in the current owner scope
- **THEN** the live-analysis form SHALL present open-existing, incremental-sync, and full-rerun choices instead of silently starting a new full import

#### Scenario: Incremental sync starts from existing workspace
- **WHEN** the user chooses incremental sync for an existing workspace with no active import
- **THEN** the live-analysis flow SHALL start a `since_last_sync` import for that workspace and route the user to the workspace progress surface

#### Scenario: Full rerun remains intentional
- **WHEN** the user chooses full re-analysis for an existing workspace
- **THEN** the live-analysis flow SHALL label the action as a full rerun and route progress to the existing workspace rather than creating an ambiguous duplicate destination

#### Scenario: Active import changes available actions
- **WHEN** repository lookup reports a queued or running import for the existing workspace
- **THEN** the live-analysis flow SHALL guide the user to the active workspace/job and SHALL NOT present duplicate repeat-run actions as normal primary actions

### Requirement: Live analysis repeat-run copy is access-source aware
The live-analysis entry flow SHALL preserve public, GitHub App-backed, and token-backed private access context when presenting repeat-run actions.

#### Scenario: Installation-backed workspace labels sync source
- **WHEN** lookup finds an installation-backed imported workspace
- **THEN** live-analysis repeat-run copy SHALL identify the GitHub App-backed access source before offering sync or rerun actions

#### Scenario: Token-backed workspace labels private source
- **WHEN** lookup finds a token-backed private imported workspace
- **THEN** live-analysis repeat-run copy SHALL identify the private access-source status without exposing credential material

#### Scenario: Missing private access does not become repeat-run
- **WHEN** lookup determines that private access setup is required before import can proceed
- **THEN** the live-analysis entry flow SHALL show setup guidance rather than presenting open/sync/rerun actions for a workspace it cannot access
