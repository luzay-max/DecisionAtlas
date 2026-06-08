## ADDED Requirements

### Requirement: Rehearsal includes package verification evidence
The self-hosted delivery rehearsal SHALL include self-hosted package verification evidence before claiming package handoff readiness.

#### Scenario: Package verification is available
- **WHEN** a self-hosted delivery rehearsal claims a package is ready for operator handoff
- **THEN** the rehearsal SHALL reference package manifest path, package verification JSON/Markdown, package status, and any blocking or operator-guided lanes

#### Scenario: Package verification is missing
- **WHEN** a self-hosted delivery rehearsal is completed without package verification evidence
- **THEN** the rehearsal SHALL classify package handoff readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim clean offline package readiness

#### Scenario: Package verification has warnings
- **WHEN** package verification reports `warning`, `blocking`, `operator_guided`, `known_limitation`, or `not_provided`
- **THEN** the rehearsal summary SHALL preserve those states and list the required follow-up before customer handoff
