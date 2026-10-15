## ADDED Requirements

### Requirement: Delivery rehearsal references real continuity evidence
The self-hosted delivery rehearsal SHALL reference real backup/restore/upgrade rehearsal evidence before claiming tested continuity readiness.

#### Scenario: Real continuity evidence is supplied
- **WHEN** a self-hosted delivery rehearsal claims tested backup, restore, upgrade, or rollback readiness
- **THEN** the rehearsal SHALL reference real continuity evidence JSON or Markdown, scratch scope, restore validation status, post-upgrade status, rollback plan status, blockers, and limitations

#### Scenario: Real continuity evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without real continuity rehearsal evidence
- **THEN** the rehearsal SHALL classify tested continuity readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that backup, restore, upgrade, or rollback mechanics have been exercised
