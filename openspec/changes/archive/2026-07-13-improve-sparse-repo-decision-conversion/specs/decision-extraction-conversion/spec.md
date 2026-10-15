## ADDED Requirements

### Requirement: Decision extraction conversion distinguishes sparse recovery outcomes
Decision extraction conversion SHALL distinguish ordinary full-extraction outcomes from bounded sparse-repository recovery and SHALL preserve conversion loss reasons for both phases.

#### Scenario: Sparse recovery creates a candidate
- **WHEN** a grounded candidate is created by the sparse recovery phase
- **THEN** extraction summary counters SHALL increment recovered-candidate and recovery-attempt counts
- **AND** normal created-candidate totals SHALL remain internally consistent.

#### Scenario: Sparse recovery remains null
- **WHEN** all bounded sparse recovery attempts return `null_decision`
- **THEN** extraction summaries SHALL retain `null_decision` as a residual conversion loss
- **AND** the import SHALL remain successful but evidence-limited.
