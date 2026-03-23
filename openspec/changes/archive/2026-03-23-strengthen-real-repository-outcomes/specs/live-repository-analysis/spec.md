## MODIFIED Requirements

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, and imported-workspace readiness so users can interpret live-analysis results correctly and know the strongest next action.

#### Scenario: Thin repository yields insufficient evidence
- **WHEN** a live analysis job completes but produces few or no candidate decisions because the repository lacks enough decision evidence
- **THEN** the system SHALL surface that outcome as insufficient evidence rather than implying the pipeline failed

#### Scenario: Review-ready workspace yields actionable outcome
- **WHEN** a live analysis job completes and the imported workspace contains reviewable candidate decisions
- **THEN** the system SHALL expose enough outcome context for the product to recommend review as the next action

#### Scenario: Runtime failure yields explicit failure context
- **WHEN** a live analysis job fails because of provider, network, or import execution errors
- **THEN** the system SHALL expose a failure summary that identifies the failing stage and broad failure category
