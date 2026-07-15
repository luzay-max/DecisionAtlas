## ADDED Requirements

### Requirement: Customer-host v2 can feed full-chain rehearsal
Customer-host v2 evidence SHALL be usable as a source lane for full-chain random repository release rehearsal.

#### Scenario: Customer-host v2 evidence is supplied
- **WHEN** full-chain rehearsal receives customer-host v2 JSON or Markdown
- **THEN** it SHALL preserve host proof level, status, lane counts, blockers, and limitations.

#### Scenario: Customer-host v2 evidence is template-only
- **WHEN** customer-host v2 evidence was generated from an example or operator-filled template
- **THEN** the full-chain bundle SHALL preserve the template limitation and SHALL NOT claim final customer-controlled host validation.
