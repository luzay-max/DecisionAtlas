# v0-3-release-candidate-baseline Specification

## Purpose
TBD - created by archiving change prepare-v0-3-release-candidate-baseline. Update Purpose after archive.
## Requirements
### Requirement: v0.3 release candidate has a frozen baseline
The system SHALL define a v0.3 release-candidate baseline that records the intended tag, final tag target commit, shipped capability boundary, known limitations, and actual local and remote tag status before v0.4 follow-up product-value work begins.

#### Scenario: RC baseline identifies tag and commit
- **WHEN** the v0.3 release candidate is finalized
- **THEN** release-facing artifacts SHALL identify the tag name, the final tag target commit, and the validation evidence for that commit

#### Scenario: RC baseline lists shipped platform capabilities
- **WHEN** release notes describe the v0.3 release candidate
- **THEN** they SHALL summarize login/session recovery, owner-scope switching, role gates, GitHub App installation binding, private repository access binding, hosted demo operator flow, and imported workspace readiness as shipped baseline capabilities

#### Scenario: RC baseline lists known limitations
- **WHEN** release notes or release-facing docs describe the v0.3 release candidate
- **THEN** they SHALL explicitly state that full SaaS org management, secret vault, GitHub Marketplace/OAuth self-service installation, billing, and multi-user collaborative review are not part of the RC baseline

#### Scenario: RC tag is created and pushed
- **WHEN** canonical validation passes for the final release-candidate commit and the release commit is clean
- **THEN** maintainers SHALL create the `v0.3.0-rc.1` tag on that commit and push the tag to `origin`

#### Scenario: Tag status stays explicit before and after finalization
- **WHEN** the tag has not yet been created
- **THEN** release-facing docs SHALL say the tag is not created yet
- **WHEN** the tag has been created and pushed
- **THEN** release-facing docs SHALL record that local and remote tag status instead of leaving the RC as only an intended tag

### Requirement: v0.3 release docs align on current product boundary
The system SHALL keep release-facing documentation aligned so maintainers and users see the same v0.3 capability boundary across README, quick start, deployment, FAQ, release notes, and release checklist content.

#### Scenario: Entry docs describe current startup paths
- **WHEN** a reader follows README or quick start instructions for v0.3
- **THEN** those docs SHALL identify the supported demo stack, real stack, and canonical validation commands without referencing removed or obsolete scripts as current entry points

#### Scenario: Entry docs describe platformized access flows
- **WHEN** a reader reviews v0.3 product capability docs
- **THEN** those docs SHALL explain that login/scope, GitHub App installation binding, and private repository access binding are productized operator/admin flows

#### Scenario: English and Chinese docs preserve the same RC meaning
- **WHEN** both English and Chinese release-facing docs exist for the same topic
- **THEN** they SHALL communicate the same v0.3 baseline, startup paths, validation path, and limitation categories

### Requirement: v0.3 release candidate records validation evidence
The system SHALL record canonical validation evidence for the final release-candidate commit before the v0.3 release candidate is treated as tagged and ready for v0.4 follow-up work.

#### Scenario: Canonical validation result is recorded
- **WHEN** `scripts/ci/pre-release.ps1` passes for the final v0.3 release-candidate commit
- **THEN** release-facing notes or checklist SHALL record the command, result, timestamp, and commit used for validation

#### Scenario: Validation failure blocks tag readiness
- **WHEN** the canonical release validation fails
- **THEN** the release candidate SHALL NOT be tagged or described as tag-ready until the blocker is resolved and validation is rerun

#### Scenario: OpenSpec validation is recorded
- **WHEN** the release candidate is finalized after OpenSpec-driven changes
- **THEN** release-facing notes or checklist SHALL record that `openspec validate --all --strict` passed for the baseline being tagged
