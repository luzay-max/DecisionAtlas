## ADDED Requirements

### Requirement: Real-stack startup distinguishes seed and reset behavior
The system SHALL distinguish non-destructive real-stack startup seeding from explicit seeded demo reset behavior so local startup remains safe while consumed demo state remains recoverable.

#### Scenario: Default startup is non-destructive
- **WHEN** a maintainer starts the real stack without an explicit reset option
- **THEN** startup SHALL run migrations and non-destructive setup without implicitly deleting or rebuilding an existing `demo-workspace`

#### Scenario: Explicit recovery restores seeded demo lane
- **WHEN** a maintainer requests explicit seeded demo recovery for the real stack
- **THEN** the workflow SHALL restore the guided demo lane to the seeded walkthrough state without implicitly deleting imported workspaces

#### Scenario: Startup guidance explains stale demo state
- **WHEN** real-stack documentation describes startup behavior
- **THEN** it SHALL explain that an existing consumed demo workspace may require explicit reset or reseed before a stable guided walkthrough

### Requirement: Real-stack validation includes migration revision guard
The system SHALL include Alembic revision ID length validation in the expected real-stack hardening validation set.

#### Scenario: Migration revision IDs fit default version table
- **WHEN** real-stack or migration validation is run for this change
- **THEN** validation SHALL include a deterministic check that Alembic revision identifiers fit the default migration version table length

#### Scenario: Migration troubleshooting references guard
- **WHEN** documentation describes migration failures caused by revision ID length
- **THEN** it SHALL point maintainers to the deterministic migration revision length check
