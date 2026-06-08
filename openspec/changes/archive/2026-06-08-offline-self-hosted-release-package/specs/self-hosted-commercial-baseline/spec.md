## ADDED Requirements

### Requirement: Self-hosted commercial claims reference package artifacts
The self-hosted commercial baseline SHALL require customer-facing package claims to reference generated package artifacts and operator runbooks.

#### Scenario: Customer handoff references package manifest
- **WHEN** documentation, release notes, or customer handoff material claims that DecisionAtlas is packaged for self-hosted evaluation
- **THEN** the material SHALL reference a package manifest, package verification evidence, setup guide, environment template, and backup/restore/upgrade runbook coverage

#### Scenario: Package claim preserves support boundary
- **WHEN** a self-hosted package is described commercially
- **THEN** the documentation SHALL distinguish package contents from paid support, custom enterprise work, runtime license enforcement, managed hosted operations, and SaaS capabilities

#### Scenario: Missing package artifacts limit claim strength
- **WHEN** package manifest or package verification evidence is missing
- **THEN** the commercial baseline SHALL require the handoff to disclose the missing artifact and avoid claiming clean package readiness
