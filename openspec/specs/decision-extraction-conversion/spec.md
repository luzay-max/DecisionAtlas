## Purpose
Define how screened-in artifacts are converted into decision candidates with artifact context preserved.
## Requirements
### Requirement: Screened-in artifacts use artifact-aware full extraction
The system SHALL use artifact-aware full extraction behavior for screened-in imported artifacts so long-form docs, high-signal PRs, and lighter-weight issue or commit evidence are not forced through one identical extraction path, and SHALL allow one bounded recovery extraction attempt when the first conversion pass fails for recoverable reasons on otherwise strong screened-in evidence.

#### Scenario: Long-form rationale document uses document-oriented extraction
- **WHEN** a screened-in imported artifact belongs to a rationale-bearing document family such as architecture, migration, rollout, ADR, release, or operations material
- **THEN** the system SHALL use a full extraction strategy tailored to that long-form rationale context rather than a generic lightweight path

#### Scenario: High-signal PR uses PR-oriented extraction
- **WHEN** a screened-in imported artifact is a pull request with explicit choice, rationale, or tradeoff content
- **THEN** the system SHALL use a full extraction strategy that treats the PR description as decision evidence rather than generic long-form documentation

#### Scenario: Recoverable first-pass conversion gets one bounded retry
- **WHEN** a screened-in imported artifact still shows strong decision signal after the first extraction attempt fails for a recoverable reason such as weak artifact-family fit, partial structure, or insufficiently grounded local context
- **THEN** the system SHALL run one bounded recovery extraction attempt using a more conversion-oriented payload before classifying that artifact as conversion loss

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
The system SHALL record why screened-in artifacts fail to become candidate decisions so imported runs can distinguish low-signal evidence from low-yield extraction conversion, and SHALL preserve the final categorized reason after any bounded recovery attempt is exhausted.

#### Scenario: Screened-in artifact produces no candidate
- **WHEN** a screened-in artifact completes its allowed extraction attempts without producing a candidate
- **THEN** the system SHALL record a categorized conversion-loss reason such as null decision, invalid JSON, missing required fields, ungrounded quote, timeout, or request failure instead of silently discarding the artifact

#### Scenario: Recovery-aware conversion failure remains diagnosable
- **WHEN** a screened-in artifact fails both the primary extraction pass and the bounded recovery pass
- **THEN** the system SHALL preserve a final conversion-loss reason that still explains why candidate creation failed after the refined conversion path was attempted

#### Scenario: Imported run reports candidate-yield counters
- **WHEN** an imported extraction run completes
- **THEN** the run summary SHALL include enough counters to compare screened-in artifacts, full extraction attempts, candidate creations, and categorized conversion losses for the final conversion path

### Requirement: Conversion diagnostics distinguish valid output from valuable candidate
The extraction conversion path SHALL distinguish candidates that are structurally valid from candidates that are valuable enough to serve as imported review baseline candidates.

#### Scenario: Structurally valid but low-value candidate is diagnosable
- **WHEN** extraction creates a candidate with weak decision specificity, thin grounding, or unclear provenance
- **THEN** diagnostics SHALL preserve enough context for review and validation surfaces to label the candidate as low-value or thin rather than silently treating it as strong

#### Scenario: Strong converted candidate preserves reviewer context
- **WHEN** extraction creates a candidate with clear decision content and grounded source refs
- **THEN** conversion output SHALL preserve enough artifact and source-ref context for the review card to show why it is a good baseline candidate

#### Scenario: Quality diagnostics remain bounded
- **WHEN** conversion diagnostics are generated
- **THEN** they SHALL use bounded categories and counters rather than raw provider prose or repository-specific hard-coded labels

### Requirement: Decision extraction conversion distinguishes sparse recovery outcomes
Decision extraction conversion SHALL distinguish ordinary full-extraction outcomes from bounded sparse-repository recovery and SHALL preserve conversion loss reasons for both phases.

#### Scenario: Sparse recovery creates a candidate
- **WHEN** a grounded candidate is created by the sparse recovery phase
- **THEN** extraction summary counters SHALL increment recovered-candidate and recovery-attempt counts
- **AND** normal created-candidate totals SHALL remain internally consistent.

#### Scenario: Sparse recovery remains null
- **WHEN** all bounded sparse recovery attempts return `null_decision`
- **THEN** extraction summaries SHALL retain `null_decision` as a residual conversion loss
- **AND** the import SHALL remain successful but evidence-limited.
