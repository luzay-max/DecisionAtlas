## ADDED Requirements

### Requirement: Self-hosted package includes pilot delivery kit references
The self-hosted release package SHALL include or reference pilot customer delivery kit materials for external evaluation.

#### Scenario: Package includes pilot materials
- **WHEN** a self-hosted package is built for external pilot evaluation
- **THEN** the package SHALL include the pilot delivery kit entry point, deployment checklist, demo script, customer FAQ, tier comparison, and delivery email template

#### Scenario: Package verifier records pilot kit lane
- **WHEN** package verification evaluates a self-hosted package
- **THEN** it SHALL record whether pilot delivery kit materials are present or explicitly operator-guided
