## ADDED Requirements

### Requirement: Pilot delivery kit can be assembled into a trial package
The pilot customer delivery kit SHALL be usable as source material for a generated pilot customer trial package.

#### Scenario: Trial package assembly runs
- **WHEN** the pilot customer trial package collector runs
- **THEN** it SHALL require the delivery kit entry point, demo script, deployment checklist, FAQ, tier comparison, delivery email template, commercial materials, proposal kit, private-repo evidence template, package guide, and support boundary.

#### Scenario: Delivery material is missing
- **WHEN** required delivery material is missing
- **THEN** the generated trial package SHALL mark the missing material as `blocking`.
