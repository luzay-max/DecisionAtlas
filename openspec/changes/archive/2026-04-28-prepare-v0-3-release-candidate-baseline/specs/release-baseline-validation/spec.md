## ADDED Requirements

### Requirement: Release baseline validation supports release candidates
The system SHALL support release-candidate baseline preparation in addition to final version baselines, using the same canonical validation entrypoint and explicit tag-readiness evidence.

#### Scenario: Release candidate uses canonical validation
- **WHEN** a maintainer prepares a release-candidate baseline such as `v0.3.0-rc.1`
- **THEN** the project SHALL use the canonical local release validation path rather than inventing a separate ad hoc RC command set

#### Scenario: Release candidate records non-final status
- **WHEN** release-facing docs describe a release-candidate baseline
- **THEN** they SHALL identify it as a release candidate and SHALL NOT imply that it is a final production SaaS release

#### Scenario: Later validation can compare against the RC
- **WHEN** follow-up hosted preview, real-stack validation, GitHub App sync, or private access hardening work begins
- **THEN** the release-candidate baseline SHALL provide a stable reference point for comparing later behavior and validation results
