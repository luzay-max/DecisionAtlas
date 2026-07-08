# real-repo-core-loop-quality Specification

## Purpose
TBD - created by archiving change improve-real-repo-core-loop-quality. Update Purpose after archive.
## Requirements
### Requirement: Core-loop quality gaps are categorized
The system SHALL categorize real repository core-loop quality gaps as product-controlled, operator/setup-driven, external dependency, not-provided, or blocking.

#### Scenario: Import is still waiting
- **WHEN** a real repository workspace exists but import setup reports `benchmark_ready=false` or next action `wait_for_import`
- **THEN** downstream diagnosis SHALL expose that the primary action is operator/setup continuation rather than claiming the repository is product-clean or product-failed.

#### Scenario: Product quality work remains
- **WHEN** review, why-search, drift, or guardrail lanes are incomplete for reasons other than setup waiting or missing proof
- **THEN** the diagnosis SHALL count those lanes as product-controlled quality actions with bounded action names.

### Requirement: Quality summaries are release-readable
The system SHALL expose aggregate quality counts that release evidence and warning-lane reduction can consume.

#### Scenario: Multi-repo diagnosis is generated
- **WHEN** multi-repo diagnosis summarizes repository core-loop results
- **THEN** it SHALL include product action count, operator action count, external action count, not-provided action count, and blocking action count.

#### Scenario: Markdown evidence is generated
- **WHEN** multi-repo or warning-reduction Markdown is written
- **THEN** it SHALL show the quality/action split without embedding secrets, raw source, or raw model output.

