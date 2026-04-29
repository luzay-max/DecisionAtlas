## MODIFIED Requirements

### Requirement: Release notes define the version baseline
The system SHALL include release notes for each prepared version baseline that summarize shipped capabilities, validation evidence, supported scope, known limitations, and final tag status once the version baseline has been tagged.

#### Scenario: Release notes summarize shipped capabilities
- **WHEN** a version baseline such as `v0.2.2` or a release candidate such as `v0.3.0-rc.1` is prepared
- **THEN** release notes SHALL summarize the material shipped capabilities since the previous baseline without requiring readers to inspect git history

#### Scenario: Release notes preserve limitation clarity
- **WHEN** release notes describe a version baseline
- **THEN** they SHALL clearly state current limitations such as auth/productized multi-user support, hosted demo status, full GitHub App onboarding, private repository productization, semantic drift conservatism, and imported workspace sparsity

#### Scenario: Release notes identify tag readiness
- **WHEN** the canonical validation path passes for a prepared version baseline
- **THEN** release notes or release checklist SHALL identify the intended tag name and commit readiness for that release baseline

#### Scenario: Release notes identify final tag status
- **WHEN** a prepared version baseline has been tagged locally and pushed to the remote
- **THEN** release notes or release checklist SHALL identify the final tag target commit and remote tag status

### Requirement: Release baseline validation supports release candidates
The system SHALL support release-candidate baseline preparation in addition to final version baselines, using the same canonical validation entrypoint, explicit tag-readiness evidence, and final tag verification when the release candidate is actually tagged.

#### Scenario: Release candidate uses canonical validation
- **WHEN** a maintainer prepares a release-candidate baseline such as `v0.3.0-rc.1`
- **THEN** the project SHALL use the canonical local release validation path rather than inventing a separate ad hoc RC command set

#### Scenario: Release candidate records non-final status
- **WHEN** release-facing docs describe a release-candidate baseline
- **THEN** they SHALL identify it as a release candidate and SHALL NOT imply that it is a final production SaaS release

#### Scenario: Later validation can compare against the RC
- **WHEN** follow-up hosted preview, real-stack validation, GitHub App sync, private access hardening, real-repository quality, or governance-layer work begins
- **THEN** the release-candidate baseline SHALL provide a stable reference point for comparing later behavior and validation results

#### Scenario: Release candidate verifies pushed tag
- **WHEN** a release candidate is finalized as a Git tag
- **THEN** maintainers SHALL verify that the tag exists locally and on `origin` before treating the release candidate as sealed
