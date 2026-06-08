## ADDED Requirements

### Requirement: Public GitHub rehearsal imports or reuses workspace before benchmark
The live repository analysis flow SHALL provide an operator-guided rehearsal path that imports or reuses the expected workspace for a selected public GitHub repository before benchmark validation claims repository-level evidence.

#### Scenario: Public repository workspace is missing before rehearsal
- **WHEN** the operator starts the public GitHub rehearsal for a curated repository whose workspace does not exist in the current owner scope
- **THEN** the rehearsal SHALL attempt the normal public import path and report whether the workspace was created, remained missing, or failed for a bounded provider or local-stack reason

#### Scenario: Public repository workspace already exists
- **WHEN** the operator starts the public GitHub rehearsal for a curated repository whose workspace already exists in the current owner scope
- **THEN** the rehearsal SHALL reuse the existing workspace and report reuse instead of creating an ambiguous duplicate import

#### Scenario: Rehearsal cannot reach GitHub or local services
- **WHEN** the public GitHub rehearsal cannot reach GitHub, the API, or the engine
- **THEN** the rehearsal SHALL classify the lane as operator-guided or provider/local-stack failure rather than claiming repository analysis success
