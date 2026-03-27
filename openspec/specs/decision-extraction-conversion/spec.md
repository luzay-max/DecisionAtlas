## ADDED Requirements

### Requirement: Screened-in artifacts use artifact-aware full extraction
The system SHALL use artifact-aware full extraction behavior for screened-in imported artifacts so long-form docs, high-signal PRs, and lighter-weight issue or commit evidence are not forced through one identical extraction path.

#### Scenario: Long-form rationale document uses document-oriented extraction
- **WHEN** a screened-in imported artifact belongs to a rationale-bearing document family such as architecture, migration, rollout, or ADR material
- **THEN** the system SHALL use a full extraction strategy tailored to long-form rationale documents

#### Scenario: High-signal PR uses PR-oriented extraction
- **WHEN** a screened-in imported artifact is a pull request with explicit choice, rationale, or tradeoff content
- **THEN** the system SHALL use a full extraction strategy that treats the PR description as decision evidence rather than generic long-form documentation

### Requirement: Full extraction can salvage decision-like structured output
The system SHALL distinguish between true non-decision outputs and recoverable partial extraction outputs so screened-in artifacts are not discarded solely because the first structured response is imperfect, and SHALL preserve enough grounded evidence from valid outputs to avoid leaving those decisions under-supported downstream.

#### Scenario: Core decision fields are present
- **WHEN** the full extraction response contains enough core decision fields and grounded evidence to describe a reviewable engineering decision
- **THEN** the system SHALL normalize and persist a candidate decision even if optional fields or formatting details are incomplete

#### Scenario: Response lacks sufficient decision structure
- **WHEN** the full extraction response does not contain enough grounded decision structure to create a trustworthy candidate
- **THEN** the system SHALL skip candidate creation and record a conversion-loss reason instead of persisting a weak candidate

#### Scenario: Valid decision still has thin grounded support
- **WHEN** the extraction response is good enough to create a decision but grounding only yields a single retained source ref from evidence that should support more
- **THEN** the system SHALL classify that outcome separately from general extraction failure so conversion diagnostics can identify source-ref coverage limits

### Requirement: Conversion-loss reasons are recorded for screened-in artifacts
The system SHALL record why screened-in artifacts fail to become candidate decisions so imported runs can distinguish low-signal evidence from low-yield extraction conversion.

#### Scenario: Screened-in artifact produces no candidate
- **WHEN** a screened-in artifact completes full extraction without producing a candidate
- **THEN** the system SHALL record a categorized conversion-loss reason such as null decision, invalid JSON, missing required fields, ungrounded quote, timeout, or request failure

#### Scenario: Imported run reports candidate-yield counters
- **WHEN** an imported extraction run completes
- **THEN** the run summary SHALL include enough counters to compare screened-in artifacts, full extraction attempts, candidate creations, and categorized conversion losses
