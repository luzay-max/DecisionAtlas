## ADDED Requirements

### Requirement: Delivery rehearsal includes clean install evidence
The self-hosted delivery rehearsal SHALL include clean install rehearsal evidence before claiming external operator trial readiness.

#### Scenario: Clean install evidence is available
- **WHEN** a self-hosted delivery rehearsal claims external operator trial readiness
- **THEN** the rehearsal summary SHALL reference clean install rehearsal JSON/Markdown, clean package copy path, package verification status, evidence family statuses, and any blockers or operator-guided lanes

#### Scenario: Clean install evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without clean install rehearsal evidence
- **THEN** the rehearsal SHALL classify external operator trial readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that the package has been validated in a clean install flow
