## MODIFIED Requirements

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
