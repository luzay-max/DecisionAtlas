## ADDED Requirements

### Requirement: Pilot kit references sales enablement materials
The pilot customer delivery kit SHALL include or reference sales enablement materials for external evaluation.

#### Scenario: Pilot kit verification runs
- **WHEN** pilot customer delivery kit verification is executed
- **THEN** it MUST require the sales page draft, one-page brief, and use-case materials

#### Scenario: Customer-facing material is incomplete
- **WHEN** a required sales enablement material is missing or omits key boundaries
- **THEN** verification MUST return a blocking status
