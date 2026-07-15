## MODIFIED Requirements

### Requirement: Fixed real repository trend pool
The system SHALL define a source-controlled fixed real repository trend pool that identifies the public repositories expected in release benchmark trend evidence.

#### Scenario: Pool validates without live services
- **WHEN** the fixed trend pool is validated during local or CI checks
- **THEN** validation MUST succeed without requiring GitHub network access, imported workspaces, model providers, or private repository credentials

#### Scenario: Pool records release intent
- **WHEN** an operator opens the fixed trend pool
- **THEN** each repository entry MUST include a stable id, repository name, workspace slug, release role, benchmark purpose, priority, operator setup status, a bounded repository profile, and sparse-conversion expectations
