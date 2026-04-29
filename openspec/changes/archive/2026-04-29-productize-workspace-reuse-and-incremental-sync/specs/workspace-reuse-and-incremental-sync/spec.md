## ADDED Requirements

### Requirement: Repeat repository analysis is gated by owner-scoped workspace state
The system SHALL resolve repeat repository analysis through owner-scoped repository lookup before starting a new import job so users can intentionally choose open-existing, incremental-sync, or full-rerun behavior.

#### Scenario: Existing workspace blocks silent full import
- **WHEN** the current owner scope looks up a repository that already maps to an imported workspace
- **THEN** the system SHALL expose the existing workspace state and SHALL NOT require the product to start a full import before showing reuse options

#### Scenario: Repeat actions are explicit
- **WHEN** an existing imported workspace is found for the current owner scope
- **THEN** the product-facing contract SHALL expose enough state to render open-existing, incremental-sync, and full-rerun actions as distinct choices

#### Scenario: Cross-scope workspace remains isolated
- **WHEN** the same repository exists only in another owner scope
- **THEN** repeat analysis lookup SHALL NOT expose that workspace as reusable state for the current owner scope

### Requirement: Active imports prevent accidental duplicate repeat runs
The system SHALL expose and enforce queued or running import state for an owner-scoped imported workspace so repeat analysis does not accidentally enqueue duplicate work.

#### Scenario: Lookup reports active import
- **WHEN** an imported workspace already has a queued or running import job
- **THEN** repository lookup SHALL report the active job state and latest job identifier in a bounded product-facing form

#### Scenario: Product discourages duplicate repeat action
- **WHEN** lookup reports an active queued or running import
- **THEN** the product SHALL disable or warn against starting another duplicate incremental sync or full rerun

#### Scenario: Backend rejects avoidable duplicate active run
- **WHEN** a direct import-start request targets a workspace that already has an active queued or running import
- **THEN** the backend SHALL return an actionable conflict or equivalent bounded state rather than blindly creating a duplicate job

### Requirement: Repeat-run sync provenance is product-readable
The system SHALL expose latest sync provenance, active sync provenance, recent sync history, and last import summary in a stable form for repeat-run product surfaces.

#### Scenario: Existing workspace shows latest sync state
- **WHEN** an imported workspace has at least one completed import or sync
- **THEN** the product-facing summary SHALL include latest sync origin, latest sync timestamp, and last import summary when available

#### Scenario: Active sync is visually distinguishable
- **WHEN** an imported workspace is currently running an incremental sync or full rerun
- **THEN** the product-facing summary SHALL expose active import status and origin distinctly from the latest completed sync

#### Scenario: Manual incremental sync and full rerun are distinguishable
- **WHEN** the product renders repeat-run choices or history
- **THEN** it SHALL label incremental sync and full re-analysis differently enough that users understand the cost and scope trade-off
