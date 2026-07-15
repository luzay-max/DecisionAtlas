## ADDED Requirements

### Requirement: Completion taskbook references post-full-chain roadmap
The completion taskbook SHALL reference the post-full-chain product roadmap after it exists.

#### Scenario: Taskbook is updated
- **WHEN** the post-full-chain roadmap is created
- **THEN** the taskbook SHALL cite it and list the next evidence-gated actions.

#### Scenario: Full-chain evidence is warning
- **WHEN** the current full-chain evidence remains warning
- **THEN** the taskbook SHALL keep final completion open and SHALL NOT claim a clean customer-ready release.
