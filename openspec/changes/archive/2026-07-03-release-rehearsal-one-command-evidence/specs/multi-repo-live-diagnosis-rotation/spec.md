## ADDED Requirements

### Requirement: Multi-repo diagnosis can feed release rehearsal
Multi-repo live diagnosis evidence SHALL be includable as a lane in the one-command release rehearsal bundle.

#### Scenario: Diagnosis evidence is provided
- **WHEN** a multi-repo diagnosis JSON path is supplied
- **THEN** the release rehearsal SHALL include selected repository IDs, aggregate counts, status, and follow-up actions.

#### Scenario: Diagnosis is run live
- **WHEN** the operator enables live multi-repo diagnosis
- **THEN** the rehearsal SHALL run diagnosis against selected real public repository metadata and include the generated evidence paths.
