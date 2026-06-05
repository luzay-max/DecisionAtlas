## ADDED Requirements

### Requirement: Engine pytest discovery boundary
The engine validation configuration SHALL constrain default pytest discovery to the canonical `services/engine/tests/` suite.

#### Scenario: Default engine pytest excludes scratch files
- **WHEN** a developer runs `uv run pytest -q` from `services/engine/`
- **THEN** pytest SHALL collect tests from `services/engine/tests/`
- **THEN** root-level scratch files under `services/engine/` SHALL NOT be collected as tests by default

### Requirement: Scratch output hygiene
The project SHALL document that ad hoc debugging scripts, generated reports, and local-only validation artifacts belong in ignored scratch locations such as `.tmp/`.

#### Scenario: Developer creates local validation artifacts
- **WHEN** a developer needs temporary scripts or generated evidence during local validation
- **THEN** project guidance SHALL direct those artifacts to `.tmp/` or another ignored scratch location
- **THEN** canonical validation commands SHALL remain stable without requiring those artifacts to be committed or deleted
