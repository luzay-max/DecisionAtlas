## ADDED Requirements

### Requirement: Multi-repo diagnosis can feed full-chain rehearsal
Multi-repo live diagnosis evidence SHALL be usable as a source lane for full-chain random repository release rehearsal.

#### Scenario: Diagnosis evidence is supplied
- **WHEN** full-chain rehearsal receives multi-repo diagnosis evidence
- **THEN** it SHALL include selected real public repository IDs, aggregate status counts, and recommended follow-up.

#### Scenario: Diagnosis evidence is absent
- **WHEN** full-chain rehearsal runs without multi-repo diagnosis evidence
- **THEN** it SHALL keep the random repository lane visible as not provided or operator guided.
