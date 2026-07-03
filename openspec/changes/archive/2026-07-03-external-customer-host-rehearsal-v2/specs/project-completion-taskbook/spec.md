## ADDED Requirements

### Requirement: Completion taskbook reflects customer-host v2 rehearsal
The completion taskbook SHALL update external customer-host readiness after customer-host v2 rehearsal exists.

#### Scenario: Customer-host v2 rehearsal is archived
- **WHEN** this change is archived
- **THEN** the taskbook SHALL cite the collector, tests, smoke evidence, documentation, and remaining product-completion gaps.

#### Scenario: Customer-host v2 evidence remains operator-guided
- **WHEN** the rehearsal runs without a real customer-controlled host template
- **THEN** the taskbook SHALL preserve the remaining external-host limitation instead of marking the full product complete.
