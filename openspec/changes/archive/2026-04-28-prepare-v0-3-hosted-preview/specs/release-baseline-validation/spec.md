## ADDED Requirements

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
