## ADDED Requirements

### Requirement: Curated real-repository validation classifies product value
The system SHALL classify curated real-repository benchmark outcomes so validation reports can distinguish useful product behavior, bounded product limitations, and operational blockers.

#### Scenario: Repository is useful now
- **WHEN** a curated imported repository has reviewable or accepted decisions, acceptable candidate quality, and focused why or drift cases that meet their bounded expectations
- **THEN** validation output SHALL classify the repository as useful for the benchmarked DecisionAtlas workflow

#### Scenario: Repository is reviewable but limited
- **WHEN** a curated imported repository has reviewable candidates but weak grounding, thin-candidate pressure, missing provenance, or limited downstream why/drift usefulness
- **THEN** validation output SHALL classify the repository as reviewable with explicit limitations rather than treating it as fully successful or failed

#### Scenario: Repository is conversion or evidence limited
- **WHEN** a curated imported repository produces enough import evidence to analyze but cannot produce useful reviewable decisions or downstream support
- **THEN** validation output SHALL classify the limitation as conversion-limited or evidence-limited with bounded supporting metrics

#### Scenario: Repository is operationally blocked
- **WHEN** validation cannot evaluate a curated repository because of missing workspace state, API availability, provider configuration, GitHub/network failure, or another setup issue
- **THEN** validation output SHALL classify the result as missing-workspace or operationally blocked rather than as product evidence

#### Scenario: Value classification remains benchmark-only
- **WHEN** value classification is computed for curated real-repository validation
- **THEN** the classification SHALL remain part of benchmark/reporting behavior and SHALL NOT introduce repository-specific product runtime behavior
