## ADDED Requirements

### Requirement: v0.3 release candidate has a frozen baseline
The system SHALL define a v0.3 release-candidate baseline that records the intended tag, validated commit, shipped capability boundary, and known limitations before follow-up platform hardening continues.

#### Scenario: RC baseline identifies tag and commit
- **WHEN** the v0.3 release candidate is prepared
- **THEN** release-facing artifacts SHALL identify the intended tag name and the commit that passed canonical validation

#### Scenario: RC baseline lists shipped platform capabilities
- **WHEN** release notes describe the v0.3 release candidate
- **THEN** they SHALL summarize login/session recovery, owner-scope switching, role gates, GitHub App installation binding, private repository access binding, hosted demo operator flow, and imported workspace readiness as shipped baseline capabilities

#### Scenario: RC baseline lists known limitations
- **WHEN** release notes or release-facing docs describe the v0.3 release candidate
- **THEN** they SHALL explicitly state that full SaaS org management, secret vault, GitHub Marketplace/OAuth self-service installation, billing, and multi-user collaborative review are not part of the RC baseline

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
The system SHALL record canonical validation evidence before the v0.3 release candidate is treated as tag-ready.

#### Scenario: Canonical validation result is recorded
- **WHEN** `scripts/ci/pre-release.ps1` passes for the v0.3 release candidate
- **THEN** release-facing notes or checklist SHALL record the command, result, and commit used for validation

#### Scenario: Validation failure blocks tag readiness
- **WHEN** the canonical release validation fails
- **THEN** the release candidate SHALL NOT be described as tag-ready until the blocker is resolved and validation is rerun
