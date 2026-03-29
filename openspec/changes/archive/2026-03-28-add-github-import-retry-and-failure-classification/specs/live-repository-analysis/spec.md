## MODIFIED Requirements

### Requirement: Live analysis reports honest outcomes
The system SHALL distinguish successful analysis, insufficient evidence, operational failure, imported-workspace readiness, existing-workspace reuse state, and clearer import failure classes so users can interpret live-analysis results correctly and know the strongest next action.

#### Scenario: Thin repository yields insufficient evidence
- **WHEN** a live analysis job completes but produces few or no candidate decisions because the repository lacks enough decision evidence
- **THEN** the system SHALL surface that outcome as insufficient evidence rather than implying the pipeline failed

#### Scenario: Review-ready workspace yields actionable outcome
- **WHEN** a live analysis job completes and the imported workspace contains reviewable candidate decisions
- **THEN** the system SHALL expose enough outcome context for the product to recommend review as the next action

#### Scenario: Runtime failure yields explicit failure context
- **WHEN** a live analysis job fails because of provider, network, or import execution errors
- **THEN** the system SHALL expose a failure summary that identifies the failing stage and broad failure category

#### Scenario: Existing repository is looked up before rerun
- **WHEN** the user enters a repository that already maps to an imported workspace
- **THEN** the live-analysis entry flow SHALL expose that reuse state before starting another import job

#### Scenario: Network failure is distinguishable from repository failure
- **WHEN** a live analysis import fails while calling GitHub
- **THEN** the system SHALL distinguish retryable-or-exhausted network failures from invalid repository or repository access failures in the resulting failure category
