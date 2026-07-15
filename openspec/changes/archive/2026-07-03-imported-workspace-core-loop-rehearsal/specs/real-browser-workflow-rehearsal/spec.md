## ADDED Requirements

### Requirement: Browser rehearsal includes imported workspace path
Browser workflow rehearsal SHALL include an imported workspace path in addition to the seeded demo path.

#### Scenario: Imported workspace UI is rehearsed
- **WHEN** browser rehearsal uses mocked API responses for determinism
- **THEN** it SHALL still display a real public GitHub repository reference and traverse imported workspace dashboard, review, why-search, drift, and evidence surfaces.

#### Scenario: Browser rehearsal uses mocked imported evidence
- **WHEN** imported workspace browser responses are mocked
- **THEN** the test or documentation SHALL state that browser proof does not replace live import or benchmark evidence.
