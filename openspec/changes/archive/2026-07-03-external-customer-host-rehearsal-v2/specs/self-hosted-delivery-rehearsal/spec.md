## ADDED Requirements

### Requirement: Delivery rehearsal references customer-host v2 evidence
Self-hosted delivery rehearsal material SHALL reference customer-host v2 evidence before claiming customer-controlled host readiness.

#### Scenario: Customer-host v2 evidence exists
- **WHEN** delivery rehearsal or handoff material claims customer-controlled host readiness
- **THEN** it SHALL reference customer-host v2 JSON or Markdown evidence, host proof level, lane statuses, blockers, and limitations.

#### Scenario: Customer-host v2 evidence is missing
- **WHEN** customer-host v2 evidence is absent
- **THEN** delivery rehearsal or handoff material SHALL preserve `not_provided` or `operator_guided` state and SHALL NOT claim verified external customer-host readiness.
