## ADDED Requirements

### Requirement: Audit trail supports compact review handoff
Collaborative review audit trail evidence SHALL be presentable as compact handoff context in the review UI.

#### Scenario: Review action is recorded
- **WHEN** a review action is available in page data or fixtures
- **THEN** the UI SHALL surface it as bounded audit context without exposing raw private source.

#### Scenario: Audit trail is incomplete
- **WHEN** audit trail data is missing or incomplete
- **THEN** the UI SHALL disclose the missing state instead of implying review history exists.
