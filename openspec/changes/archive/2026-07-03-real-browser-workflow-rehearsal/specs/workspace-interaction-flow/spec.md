## ADDED Requirements

### Requirement: Workspace interaction flow is browser-verifiable
The workspace interaction flow SHALL be verifiable through a real browser workflow, not only static page or component assertions.

#### Scenario: Browser workflow traverses workspace actions
- **WHEN** a browser rehearsal opens a workspace dashboard
- **THEN** review, why-search, drift, evidence, and return-to-dashboard actions SHALL remain reachable through visible UI controls or direct workflow links.

#### Scenario: Next action remains clear after cross-page navigation
- **WHEN** a browser rehearsal completes or pauses a review, search, drift, or evidence step
- **THEN** the page SHALL expose a clear next action back to the workspace workflow or related evidence.
