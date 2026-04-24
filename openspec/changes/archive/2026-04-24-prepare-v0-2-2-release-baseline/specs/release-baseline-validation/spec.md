## MODIFIED Requirements

### Requirement: Release baseline validation has a canonical local entrypoint
The system SHALL provide a single canonical local release baseline validation path so maintainers do not need hidden project knowledge to determine which checks represent the current branch baseline, and a release milestone SHALL record whether that canonical path passed before a tag is prepared.

#### Scenario: Release baseline validation runs the canonical check set
- **WHEN** a maintainer prepares the current branch baseline for tagging or release-style verification
- **THEN** the project SHALL provide a canonical local validation entrypoint that runs the defined baseline checks rather than relying on scattered manual command selection

#### Scenario: Release baseline validation tolerates `uv` path variance
- **WHEN** the local environment does not expose the `uv` CLI directly but does allow `python -m uv`
- **THEN** the canonical release baseline validation path SHALL still remain executable without forcing maintainers to rediscover the fallback manually

#### Scenario: Release milestone records canonical validation
- **WHEN** a release-style version baseline such as `v0.2.2` is prepared
- **THEN** the release-facing notes or checklist SHALL record the canonical validation command and its result before the tag is treated as ready

### Requirement: Release-facing docs align on baseline commands and lane boundaries
The system SHALL keep release-facing documentation aligned with the current branch baseline so readers can distinguish the stable guided demo lane from the imported real-repository lane, follow the same validation path described by the project, and understand which version milestone the current docs describe.

#### Scenario: Release-facing docs share the same validation path
- **WHEN** a maintainer reads README, quick start, or release checklist guidance before validating the branch baseline
- **THEN** those release-facing docs SHALL point back to the same canonical local validation path instead of presenting conflicting release commands

#### Scenario: Release-facing docs distinguish demo from imported validation
- **WHEN** release-facing docs describe the current product baseline
- **THEN** they SHALL describe the guided demo lane as the stable walkthrough and the imported lane as the real-capability path with bounded readiness and evidence outcomes rather than blurring the two

#### Scenario: Release-facing docs identify the current milestone
- **WHEN** the project prepares a new release baseline after shipped imported-lane improvements
- **THEN** README and release notes SHALL describe the current milestone and stage without leaving the project framed only as the older v0.2 demo-hardening baseline

#### Scenario: English and Chinese docs preserve the same release meaning
- **WHEN** release-facing docs are updated for a milestone
- **THEN** the English and Chinese entry points SHALL communicate the same current stage, stable demo lane, imported lane, and limitation categories

### Requirement: Release baseline validation covers both stable product lanes
The system SHALL define the release baseline in a way that covers both the stable guided demo lane and the bounded imported real-repository lane, and SHALL keep the distinction between required offline validation and optional operator-guided live validation explicit.

#### Scenario: Guided demo baseline is part of release validation
- **WHEN** release baseline validation is defined for the current branch
- **THEN** it SHALL include checks that confirm the guided demo path still behaves as the stable walkthrough

#### Scenario: Imported real-repo baseline is part of release validation
- **WHEN** release baseline validation is defined for the current branch
- **THEN** it SHALL include checks that confirm imported workspaces still expose bounded readiness, why, and drift outcomes rather than treating import completion alone as sufficient

#### Scenario: Optional live validation is not confused with the default gate
- **WHEN** release-facing docs mention operator-guided live real-repo validation
- **THEN** they SHALL identify it as an optional confidence layer rather than as a requirement for the default offline release baseline

## ADDED Requirements

### Requirement: Release notes define the version baseline
The system SHALL include release notes for each prepared version baseline that summarize shipped capabilities, validation evidence, supported scope, and known limitations.

#### Scenario: Release notes summarize shipped capabilities
- **WHEN** a version baseline such as `v0.2.2` is prepared
- **THEN** release notes SHALL summarize the material shipped capabilities since the previous baseline without requiring readers to inspect git history

#### Scenario: Release notes preserve limitation clarity
- **WHEN** release notes describe a version baseline
- **THEN** they SHALL clearly state current limitations such as auth/productized multi-user support, hosted demo status, full GitHub App onboarding, private repository productization, semantic drift conservatism, and imported workspace sparsity

#### Scenario: Release notes identify tag readiness
- **WHEN** the canonical validation path passes for a prepared version baseline
- **THEN** release notes or release checklist SHALL identify the intended tag name and commit readiness for that release baseline
