## ADDED Requirements

### Requirement: Delivery rehearsal references external install evidence
The self-hosted delivery rehearsal SHALL include external install evidence before claiming customer-controlled host install readiness.

#### Scenario: External install evidence is available
- **WHEN** a self-hosted delivery rehearsal claims customer-controlled host install readiness
- **THEN** the rehearsal summary SHALL reference external install evidence JSON or Markdown, external host class, package identity, lane statuses, blockers, and limitations

#### Scenario: External install evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without external install evidence
- **THEN** the rehearsal SHALL classify customer-controlled host install readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that the package has been validated on a non-developer or customer-controlled machine
