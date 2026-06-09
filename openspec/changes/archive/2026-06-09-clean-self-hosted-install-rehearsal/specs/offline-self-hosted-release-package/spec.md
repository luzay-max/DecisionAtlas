## ADDED Requirements

### Requirement: Package references clean install rehearsal
The self-hosted package SHALL document how operators can run clean install rehearsal before customer handoff.

#### Scenario: Package docs include clean rehearsal command
- **WHEN** an operator opens the self-hosted package README or package guide
- **THEN** the documentation SHALL identify the clean install rehearsal command, expected JSON and Markdown outputs, required package input, and optional source evidence inputs

#### Scenario: Package verifier notes clean rehearsal boundary
- **WHEN** package verification evidence is generated
- **THEN** the evidence SHALL state that package structure verification is not the same as clean install rehearsal and SHALL identify clean rehearsal evidence as a separate customer-readiness input
