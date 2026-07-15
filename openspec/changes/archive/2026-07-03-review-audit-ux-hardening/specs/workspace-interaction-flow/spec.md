## ADDED Requirements

### Requirement: Review flow includes next-step guidance
Workspace interaction flow SHALL include review-specific next-step guidance.

#### Scenario: Pending candidates exist
- **WHEN** pending review candidates exist
- **THEN** the review page SHALL show the next action for reviewers and the expected handoff for viewers.

#### Scenario: No candidates exist
- **WHEN** no review candidates are available
- **THEN** the review page SHALL show how to generate or import more evidence.
