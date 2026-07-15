## ADDED Requirements

### Requirement: Completion taskbook tracks pilot customer trial package
The project completion taskbook SHALL track the generated pilot customer trial package as the next step after real external host trial evidence gating.

#### Scenario: Trial package is implemented
- **WHEN** pilot customer trial package support is implemented
- **THEN** the taskbook SHALL cite the collector, generated package artifacts, tests, browser verification, and remaining real customer-machine boundary.

#### Scenario: Trial package remains warning
- **WHEN** the generated package contains warning, operator-guided, not-provided, or template-only evidence
- **THEN** the taskbook SHALL keep customer-ready completion open and SHALL NOT claim clean external pilot readiness.
