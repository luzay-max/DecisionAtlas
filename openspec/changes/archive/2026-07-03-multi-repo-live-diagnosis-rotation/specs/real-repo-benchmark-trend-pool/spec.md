## ADDED Requirements

### Requirement: Benchmark trend pool supports diagnosis rotation
The real-repo benchmark trend pool SHALL be usable for multi-repo live diagnosis selection.

#### Scenario: Diagnosis reads the pool
- **WHEN** the diagnosis script loads the trend pool
- **THEN** it SHALL use repository id, repo identity, workspace slug, priority, and setup status to select and label real repository diagnosis rows.

#### Scenario: Unknown repository is requested
- **WHEN** an operator requests a repository id not present in the pool
- **THEN** the diagnosis SHALL fail with a clear error instead of silently skipping it.
