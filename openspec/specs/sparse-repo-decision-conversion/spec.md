# sparse-repo-decision-conversion Specification

## Purpose
TBD - created by archiving change improve-sparse-repo-decision-conversion. Update Purpose after archive.
## Requirements
### Requirement: Sparse repository recovery is bounded and evidence-triggered
The system SHALL attempt sparse-repository decision recovery only after a successful import produces zero candidates and eligible high-signal evidence remains, and SHALL enforce a deterministic maximum artifact and model-attempt budget.

#### Scenario: Zero-candidate import has eligible evidence
- **WHEN** normal extraction completes with zero candidates and unprocessed high-signal artifacts contain explicit decision cues
- **THEN** the system SHALL select a deterministic, family-diverse recovery set within the configured budget
- **AND** it SHALL record that sparse recovery was eligible and attempted.

#### Scenario: Import already produced a candidate
- **WHEN** normal extraction creates one or more candidates
- **THEN** the system SHALL NOT invoke sparse-repository recovery.

#### Scenario: No eligible evidence remains
- **WHEN** normal extraction creates zero candidates but no remaining artifact satisfies sparse-recovery eligibility
- **THEN** the system SHALL preserve the zero-candidate outcome
- **AND** it SHALL record `no_eligible_evidence` without invoking the model.

### Requirement: Recovered candidates preserve grounding and review boundaries
The system SHALL apply the normal candidate schema, explicit source-quote grounding, source-reference persistence, confidence, and human review-state requirements to every sparse-recovery output.

#### Scenario: Recovery output is grounded
- **WHEN** a recovery output contains the required decision fields and a source quote that is present in the selected artifact
- **THEN** the system SHALL create a review-state `candidate` with source references
- **AND** it SHALL NOT automatically accept the candidate.

#### Scenario: Recovery output is not grounded
- **WHEN** a recovery output omits required evidence or its source quote cannot be matched to the selected artifact
- **THEN** the system SHALL reject the output
- **AND** it SHALL record a bounded rejection reason without creating a decision.

### Requirement: Sparse conversion outcomes are observable
The system SHALL emit compact sparse-recovery metrics and reason codes in import summaries and live rehearsal evidence.

#### Scenario: Recovery completes
- **WHEN** sparse recovery completes with or without a candidate
- **THEN** the summary SHALL report eligibility, attempted artifacts, evidence families, model attempts, recovered candidates, rejected outputs, and residual loss reasons.

#### Scenario: Provider fails during recovery
- **WHEN** the configured provider times out or fails during sparse recovery
- **THEN** the import SHALL preserve already imported artifacts and normal extraction outcomes
- **AND** the summary SHALL classify the recovery provider failure without fabricating a candidate.
