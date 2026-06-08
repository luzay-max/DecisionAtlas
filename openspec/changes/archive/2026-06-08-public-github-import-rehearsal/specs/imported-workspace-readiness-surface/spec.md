## ADDED Requirements

### Requirement: Public import readiness records setup path
Imported-workspace readiness evidence SHALL expose whether a public GitHub workspace was created, reused, unavailable, or still operator-guided during rehearsal.

#### Scenario: Public import creates workspace
- **WHEN** a public GitHub rehearsal creates an imported workspace
- **THEN** readiness evidence SHALL include the workspace slug, repository identifier, setup path, and bounded readiness state without requiring UI scraping

#### Scenario: Public import reuses workspace
- **WHEN** a public GitHub rehearsal reuses an existing imported workspace
- **THEN** readiness evidence SHALL identify the reuse path and preserve the workspace's current readiness state

#### Scenario: Public import remains incomplete
- **WHEN** a public GitHub rehearsal cannot create or find the workspace
- **THEN** readiness evidence SHALL retain a non-pass setup state with a bounded reason such as missing local service, provider failure, network failure, or operator setup required
