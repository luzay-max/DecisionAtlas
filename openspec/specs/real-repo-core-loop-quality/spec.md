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

### Requirement: Why and drift warnings are grounded
The system SHALL attach bounded grounding metadata to product-controlled `why_search` and `drift` warning lanes in real repository core-loop diagnosis.

#### Scenario: Why-search warning remains product-controlled
- **WHEN** a real repository diagnosis reports a `why_search` warning for a repository whose setup is complete
- **THEN** the diagnosis SHALL include a compact reason code and release-readable summary explaining whether the gap is weak why-answer support, missing accepted-decision evidence, or unknown grounding.

#### Scenario: Drift warning remains product-controlled
- **WHEN** a real repository diagnosis reports a `drift` warning for a repository whose setup is complete
- **THEN** the diagnosis SHALL include a compact reason code and release-readable summary explaining whether the gap is unresolved drift follow-up, stale/superseded evidence, missing accepted-decision evidence, or unknown grounding.

### Requirement: Grounding details flow into release evidence
The system SHALL preserve why/drift grounding details through multi-repo diagnosis and warning-lane reduction outputs.

#### Scenario: Multi-repo Markdown is generated
- **WHEN** multi-repo live diagnosis writes Markdown for repositories with `why_search` or `drift` warnings
- **THEN** the Markdown SHALL show compact grounding details without embedding secrets, raw private source, or raw model output.

#### Scenario: Warning-lane reduction is generated
- **WHEN** random repo warning-lane reduction classifies a product-controlled repository lane
- **THEN** the classified lane SHALL include compact grounding details for the product-controlled why/drift warnings so the next remediation is actionable.

### Requirement: Accepted-decision baseline is measured
The system SHALL expose accepted-decision baseline status in real repository core-loop evidence without auto-accepting candidate decisions.

#### Scenario: Accepted baseline is empty
- **WHEN** a real repository workspace has candidate decisions but zero accepted decisions
- **THEN** the core-loop evidence SHALL report an accepted baseline status of `empty` with bounded candidate and accepted counts.

#### Scenario: Accepted baseline is present
- **WHEN** a real repository workspace has one or more accepted decisions
- **THEN** the core-loop evidence SHALL report an accepted baseline status of `present` with bounded accepted-decision samples.

### Requirement: Accepted baseline explains why and drift warnings
The system SHALL include accepted baseline status in why/drift grounding details for product-controlled warning lanes.

#### Scenario: Why-search lacks accepted baseline
- **WHEN** a why-search warning uses `missing_accepted_decision_evidence`
- **THEN** its grounding evidence SHALL include accepted baseline status and accepted decision count.

#### Scenario: Drift lacks accepted baseline
- **WHEN** a drift warning uses `missing_accepted_decision_evidence`
- **THEN** its grounding evidence SHALL include accepted baseline status and accepted decision count.

### Requirement: Baseline summaries flow into release evidence
The system SHALL preserve accepted baseline summaries through multi-repo diagnosis and warning-lane reduction outputs.

#### Scenario: Multi-repo diagnosis is generated
- **WHEN** multi-repo diagnosis includes repositories with accepted baseline metadata
- **THEN** each repository result SHALL include the compact accepted baseline summary.

#### Scenario: Warning-lane reduction is generated
- **WHEN** warning-lane reduction classifies a product-controlled repository lane
- **THEN** the classified lane SHALL include accepted baseline summary when supplied by the multi-repo source.

