## ADDED Requirements

### Requirement: Live repository context is visible in browser rehearsal
The live repository analysis flow SHALL expose real repository context in browser-level rehearsal evidence when repository import or reuse behavior is tested.

#### Scenario: Public repository context appears in UI
- **WHEN** a browser rehearsal exercises public repository import, reuse, or imported workspace guidance
- **THEN** the UI SHALL display a real public GitHub repository reference or owner/name that can be traced to the tested scenario.

#### Scenario: Browser rehearsal does not replace live benchmark evidence
- **WHEN** browser rehearsal uses mocked repository responses or seeded workspace data
- **THEN** live repository benchmark and readiness evidence SHALL remain the source of truth for claims about actual GitHub import quality.
