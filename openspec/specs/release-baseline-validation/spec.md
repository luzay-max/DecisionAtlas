## ADDED Requirements

### Requirement: Release baseline validation has a canonical local entrypoint
The system SHALL provide a single canonical local release baseline validation path so maintainers do not need hidden project knowledge to determine which checks represent the current branch baseline.

#### Scenario: Release baseline validation runs the canonical check set
- **WHEN** a maintainer prepares the current branch baseline for tagging or release-style verification
- **THEN** the project SHALL provide a canonical local validation entrypoint that runs the defined baseline checks rather than relying on scattered manual command selection

#### Scenario: Release baseline validation tolerates `uv` path variance
- **WHEN** the local environment does not expose the `uv` CLI directly but does allow `python -m uv`
- **THEN** the canonical release baseline validation path SHALL still remain executable without forcing maintainers to rediscover the fallback manually

### Requirement: Release-facing docs align on baseline commands and lane boundaries
The system SHALL keep release-facing documentation aligned with the current branch baseline so readers can distinguish the stable guided demo lane from the imported real-repository lane and follow the same validation path described by the project.

#### Scenario: Release-facing docs share the same validation path
- **WHEN** a maintainer reads README, quick start, or release checklist guidance before validating the branch baseline
- **THEN** those release-facing docs SHALL point back to the same canonical local validation path instead of presenting conflicting release commands

#### Scenario: Release-facing docs distinguish demo from imported validation
- **WHEN** release-facing docs describe the current product baseline
- **THEN** they SHALL describe the guided demo lane as the stable walkthrough and the imported lane as the real-capability path with bounded readiness and evidence outcomes rather than blurring the two

### Requirement: Release baseline validation covers both stable product lanes
The system SHALL define the release baseline in a way that covers both the stable guided demo lane and the bounded imported real-repository lane.

#### Scenario: Guided demo baseline is part of release validation
- **WHEN** release baseline validation is defined for the current branch
- **THEN** it SHALL include checks that confirm the guided demo path still behaves as the stable walkthrough

#### Scenario: Imported real-repo baseline is part of release validation
- **WHEN** release baseline validation is defined for the current branch
- **THEN** it SHALL include checks that confirm imported workspaces still expose bounded readiness, why, and drift outcomes rather than treating import completion alone as sufficient
