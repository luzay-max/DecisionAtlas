# release-baseline-validation Specification

## Purpose
Define the release baseline validation contract, release-facing documentation requirements, and tag-readiness evidence needed before preparing a DecisionAtlas version baseline.
## Requirements
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
The system SHALL keep release-facing documentation aligned with the current branch baseline so readers can distinguish the stable guided demo lane from the imported real-repository lane, follow the same validation path described by the project, understand which version milestone the current docs describe, and see the current completed stage plus next planned stage without stale OpenSpec or Git status.

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

#### Scenario: Master plan reflects current completed and next stages
- **WHEN** a stage change has been completed, synced, archived, committed, and pushed
- **THEN** the master plan SHALL identify the latest baseline commit, active OpenSpec change count, completed stage, and next planned stage without stale in-progress language

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

### Requirement: Release baseline validation distinguishes confidence layers
The system SHALL distinguish mandatory canonical release validation from broader real-stack confidence validation so release gates remain deterministic while operator-recorded validation can still inform release readiness.

#### Scenario: Canonical release gate remains mandatory
- **WHEN** maintainers prepare a release or release-candidate baseline
- **THEN** the project SHALL continue to identify the canonical pre-release command as the mandatory local release gate

#### Scenario: Real-stack validation is recorded as a confidence layer
- **WHEN** maintainers perform broader v0.3 real-stack validation
- **THEN** release-facing docs or validation reports SHALL describe it as an operator-recorded confidence layer unless it has been made deterministic enough for default CI

#### Scenario: Release readiness references both layers clearly
- **WHEN** a release candidate is evaluated after real-stack validation
- **THEN** the project SHALL make clear which evidence came from the mandatory release gate and which evidence came from optional or operator-guided real-stack validation

### Requirement: Release docs distinguish hosted preview readiness from release gates
The system SHALL keep hosted preview readiness distinct from mandatory release baseline validation.

#### Scenario: Hosted preview checks are post-RC confidence
- **WHEN** release-facing docs mention hosted preview readiness
- **THEN** they SHALL describe hosted health, smoke, reset, reseed, and external walkthrough checks as post-RC confidence checks rather than replacements for the canonical release gate

#### Scenario: Canonical release gate remains primary
- **WHEN** maintainers prepare release or release-candidate validation
- **THEN** the docs SHALL continue to identify `scripts/ci/pre-release.ps1` as the mandatory deterministic local release gate

#### Scenario: Preview limitations stay visible
- **WHEN** hosted preview docs or release notes describe external availability
- **THEN** they SHALL state that the preview is not a production SaaS release and does not include SLA, billing, full org management, or unlimited real repository imports

### Requirement: Governed hosted preview remains separate from release gates
The system SHALL keep governed hosted preview readiness distinct from mandatory release baseline validation and SHALL NOT require hosted URLs, live providers, real GitHub credentials, or guardrail enforcement for the default release gate.

#### Scenario: Release docs keep canonical gate primary
- **WHEN** release-facing docs mention governed hosted preview readiness
- **THEN** they SHALL continue to identify the canonical local pre-release command as the mandatory deterministic release gate

#### Scenario: Governed preview is a confidence layer
- **WHEN** readiness reports describe governance smoke, guardrail status, hosted health, hosted smoke, or live real-repository benchmark evidence
- **THEN** they SHALL classify that evidence as a post-release-candidate confidence layer rather than as a replacement for release validation

#### Scenario: Production SaaS limits remain visible
- **WHEN** governed hosted preview readiness is summarized for a milestone
- **THEN** the summary SHALL state that the preview is not a production SaaS release and does not include billing, full organization administration, secret vault, marketplace self-service, multiplayer review, or default governance enforcement

### Requirement: Release baseline remains separate from enforcement preview
The system SHALL keep optional governance enforcement preview output separate from the default release baseline and SHALL NOT require enforcement preview success for the default local release gate.

#### Scenario: Default release gate excludes enforcement preview
- **WHEN** the canonical local release baseline runs
- **THEN** it SHALL NOT fail solely because optional governance enforcement preview output would warn or block

#### Scenario: Checklist can record preview evidence
- **WHEN** an operator prepares release or hosted-preview readiness evidence
- **THEN** the checklist MAY include optional enforcement preview status, source evidence, and human override notes as advisory readiness evidence

#### Scenario: Preview limitation is explicit
- **WHEN** release or hosted-preview documentation mentions enforcement preview
- **THEN** it SHALL state that the preview is opt-in, warning/report oriented by default, and not default CI enforcement

### Requirement: Release-facing docs distinguish development protocol from release gates
The system SHALL keep the default local governance development protocol distinct from canonical release validation and optional enforcement preview.

#### Scenario: Docs identify canonical release gate
- **WHEN** release-facing docs mention the default governance development protocol
- **THEN** they SHALL continue to identify the canonical local release gate as the mandatory deterministic release validation path

#### Scenario: Docs identify development protocol scope
- **WHEN** developers or AI agents read workflow guidance
- **THEN** the docs SHALL describe the default governance development protocol as local workflow guidance for preflight, postflight, archive, commit, and handoff behavior

#### Scenario: Docs identify enforcement preview as opt-in
- **WHEN** docs mention enforcement preview or strict exit behavior
- **THEN** they SHALL state that enforcement preview remains opt-in and is not default CI enforcement

### Requirement: Release checklist records governance protocol evidence
The system SHALL allow release and readiness records to include governance protocol evidence without making advisory guardrail status a default release blocker.

#### Scenario: Checklist can record protocol status
- **WHEN** a maintainer prepares release or readiness evidence
- **THEN** the checklist MAY record the latest protocol status, guardrail status, recommended actions, and human questions as advisory evidence

#### Scenario: Advisory status does not replace release gate
- **WHEN** protocol status is recorded in release or readiness evidence
- **THEN** the documentation SHALL state that it does not replace the canonical release baseline command

#### Scenario: Pause evidence requires human decision before positive claims
- **WHEN** protocol status reports `pause` during release or hosted-preview preparation
- **THEN** release-facing guidance SHALL require a human decision before using that status as positive readiness evidence

### Requirement: Release baseline validation can reference generated evidence bundles
Release-facing validation records SHALL be able to reference generated release evidence bundles without replacing the canonical release gate.

#### Scenario: Bundle summarizes canonical release gate
- **WHEN** a release evidence bundle includes canonical pre-release validation status
- **THEN** release-facing documentation MAY reference the bundle as supporting evidence
- **AND** the canonical pre-release validation result SHALL remain visible as its own required gate.

#### Scenario: Bundle keeps confidence layers separate
- **WHEN** the evidence bundle includes OpenSpec validation, governance guardrail status, benchmark results, and targeted test summaries
- **THEN** the bundle SHALL preserve which results are required gates and which results are advisory confidence layers.

#### Scenario: Advisory evidence requires disclosure
- **WHEN** advisory evidence reports `caution`, `warning`, `pause`, or an equivalent non-clean status
- **THEN** release-facing documentation that references the bundle SHALL disclose that status before making a positive readiness claim.

#### Scenario: Bundle does not replace manual release decision
- **WHEN** all generated evidence is present
- **THEN** the bundle SHALL support the release decision
- **AND** the bundle SHALL NOT automatically publish, archive, tag, or approve a release.

