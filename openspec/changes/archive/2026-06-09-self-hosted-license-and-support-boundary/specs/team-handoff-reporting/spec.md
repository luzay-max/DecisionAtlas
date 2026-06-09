## ADDED Requirements

### Requirement: Handoff reports disclose license and support boundary
Team handoff reports SHALL disclose license/support boundary evidence when provided.

#### Scenario: Boundary evidence is included
- **WHEN** handoff report generation receives license/support boundary evidence
- **THEN** the report SHALL summarize tier, support window, deployment scope, upgrade channel, and non-enforced runtime boundary without exposing secrets

#### Scenario: Boundary evidence is missing
- **WHEN** handoff report generation does not receive license/support boundary evidence
- **THEN** the report SHALL mark the license/support boundary section as not provided or operator-guided rather than omitting it
