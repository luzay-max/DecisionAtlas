## ADDED Requirements

### Requirement: Completion taskbook reflects imported core-loop rehearsal
The completion taskbook SHALL update core-loop status when imported workspace core-loop evidence is added.

#### Scenario: Core-loop rehearsal is implemented
- **WHEN** imported workspace core-loop rehearsal is archived
- **THEN** the taskbook SHALL cite the collector, browser rehearsal, tests, and remaining evidence boundary.

#### Scenario: Core-loop evidence is still partial
- **WHEN** live import or multi-repo proof is still not complete
- **THEN** the taskbook SHALL keep the broader real GitHub repository validation line as partial.
