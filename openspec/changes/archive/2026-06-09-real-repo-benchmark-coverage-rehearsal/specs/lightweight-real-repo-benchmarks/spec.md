## ADDED Requirements

### Requirement: Benchmark comparison workflow can be rehearsed end-to-end
The real-repo benchmark workflow SHALL support an operator-guided rehearsal that chains current report, snapshot, comparison, and trend evidence with explicit inputs.

#### Scenario: Rehearsal uses existing benchmark comparison functions
- **WHEN** the rehearsal creates comparison evidence
- **THEN** it MUST preserve existing movement labels and summary counts from the benchmark comparison workflow

#### Scenario: Rehearsal remains deterministic without live services
- **WHEN** CI tests the rehearsal workflow
- **THEN** it MUST use local fixture JSON and MUST NOT require live API, GitHub, model providers, or imported workspaces
