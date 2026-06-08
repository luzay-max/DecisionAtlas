## ADDED Requirements

### Requirement: Self-hosted package references handoff reporting
The self-hosted package SHALL document how operators can generate team handoff reports as part of delivery acceptance.

#### Scenario: Package docs include handoff report generation
- **WHEN** an operator opens the self-hosted package README or runbook
- **THEN** the documentation SHALL identify the handoff report command, expected JSON and Markdown outputs, recommended source evidence inputs, and secret-handling boundary

#### Scenario: Package verifier acknowledges handoff evidence
- **WHEN** a package verifier or readiness flow evaluates delivery evidence
- **THEN** it SHALL be able to record whether team handoff report evidence was provided, not provided, operator-guided, or blocking
