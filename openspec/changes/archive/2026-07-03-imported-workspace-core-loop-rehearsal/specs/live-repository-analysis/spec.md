## ADDED Requirements

### Requirement: Imported repository analysis can feed core-loop rehearsal
Live repository analysis SHALL provide enough repository and workspace context for imported workspace core-loop rehearsal.

#### Scenario: Import rehearsal produced a workspace
- **WHEN** public GitHub import rehearsal returns a created or reused workspace
- **THEN** imported workspace core-loop rehearsal SHALL be able to use that workspace slug and repository identity as input.

#### Scenario: Import rehearsal is not ready
- **WHEN** public GitHub import rehearsal reports provider failure, local stack failure, operator-guided, or missing workspace
- **THEN** imported workspace core-loop rehearsal SHALL preserve that setup state and SHALL NOT claim the core loop passed.
