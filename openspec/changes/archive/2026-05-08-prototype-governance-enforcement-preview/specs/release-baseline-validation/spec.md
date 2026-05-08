## ADDED Requirements

### Requirement: Release baseline remains separate from enforcement preview
The system SHALL keep optional governance enforcement preview output separate from the default release baseline and SHALL NOT require enforcement preview success for the default local release gate.

#### Scenario: Default release gate excludes enforcement preview
- **WHEN** the canonical local release baseline runs
- **THEN** it SHALL NOT fail solely because optional governance enforcement preview output would warn or block

#### Scenario: Checklist can record preview evidence
- **WHEN** an operator prepares release or hosted-preview readiness evidence
- **THEN** the checklist MAY include optional enforcement preview status, source evidence, and human override notes as advisory readiness evidence

#### Scenario: Preview limitation is explicit
- **WHEN** release or hosted-preview documentation mentions enforcement preview
- **THEN** it SHALL state that the preview is opt-in, warning/report oriented by default, and not default CI enforcement
