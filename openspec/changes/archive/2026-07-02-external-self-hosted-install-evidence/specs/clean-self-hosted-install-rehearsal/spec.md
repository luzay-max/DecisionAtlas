## ADDED Requirements

### Requirement: Clean install rehearsal distinguishes local clean checks from external host evidence
The clean self-hosted install rehearsal SHALL disclose that local clean workspace checks are not a substitute for external or customer-controlled host install evidence.

#### Scenario: Local clean rehearsal is generated without external evidence
- **WHEN** clean install rehearsal evidence is generated without external install evidence
- **THEN** the report SHALL preserve local clean install status but SHALL mark external/customer-host install evidence as `not_provided` or `operator_guided`

#### Scenario: External evidence is referenced
- **WHEN** clean install rehearsal evidence receives an external install evidence JSON or Markdown path
- **THEN** the report SHALL reference the external evidence status and limitations without copying raw external evidence content
