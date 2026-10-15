## ADDED Requirements

### Requirement: Customer-host v2 feeds real external host trial evidence
Customer-host v2 evidence SHALL be usable as a source for the stricter real external host trial evidence gate.

#### Scenario: Customer-host v2 evidence is supplied to the trial gate
- **WHEN** real external host trial evidence receives customer-host v2 JSON
- **THEN** it SHALL preserve customer-host v2 status, host proof level, lane counts, blockers, limitations, and warnings.

#### Scenario: Customer-host v2 evidence is template-like
- **WHEN** customer-host v2 evidence was generated from an example template, placeholder input, or local-only proof
- **THEN** the real external host trial gate SHALL keep the final trial evidence non-clean and SHALL NOT claim real external/customer-controlled host validation.
