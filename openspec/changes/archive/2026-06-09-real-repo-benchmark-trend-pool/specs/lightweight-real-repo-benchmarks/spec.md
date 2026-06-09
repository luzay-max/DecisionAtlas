## ADDED Requirements

### Requirement: Benchmark comparisons can feed fixed-pool trend evidence
The real repository benchmark comparison output SHALL be usable as input for fixed-pool benchmark trend evidence.

#### Scenario: Comparison rows match trend pool ids
- **WHEN** comparison rows contain repository ids that match the fixed trend pool
- **THEN** downstream trend evidence MUST classify those repositories as covered and retain their comparison movement labels

#### Scenario: Comparison omits a pool repository
- **WHEN** a fixed pool repository is absent from the comparison rows
- **THEN** downstream trend evidence MUST mark that repository as missing from current trend coverage

### Requirement: Benchmark trend validation remains offline
The benchmark trend workflow SHALL be validatable without live repository imports.

#### Scenario: CI validates trend evidence
- **WHEN** CI runs trend-pool tests
- **THEN** the tests MUST use deterministic local JSON fixtures and MUST NOT require GitHub, model-provider, or local workspace availability
