## MODIFIED Requirements

### Requirement: Real repository outcomes report decision-value quality
The system SHALL evaluate imported real-repository outcomes not only by readiness state, but also by whether reviewable candidate decisions are valuable, grounded, and useful for establishing the first accepted baseline, using the same candidate quality labels and reason categories exposed in the review product.

#### Scenario: Validation records candidate value observations
- **WHEN** an operator validates a curated imported repository
- **THEN** the report SHALL include candidate-quality observations such as reviewable candidate count, strong/partial/thin label distribution, thin-evidence pressure, provenance availability, previewable source-ref availability, and whether a first accepted baseline appears achievable

#### Scenario: Low-value candidates are not treated as equal to strong candidates
- **WHEN** an imported workspace contains candidates with weak grounding or unclear provenance
- **THEN** the product or validation report SHALL distinguish those candidates from strongly grounded candidates instead of treating all candidates as equally review-ready

#### Scenario: First baseline usefulness is recorded
- **WHEN** a reviewer accepts the first imported decision in a real repository workspace
- **THEN** validation output SHALL be able to record whether that baseline unlocks a meaningful why/drift path for matching questions

#### Scenario: Quality report explains thin pressure
- **WHEN** real-repository validation reports a high thin-candidate ratio
- **THEN** the report SHALL expose whether thin pressure is driven by missing source refs, missing previewable quotes, missing provenance, low confidence, or another bounded reason category

#### Scenario: Fixture quality checks remain bounded
- **WHEN** default benchmark fixture validation checks candidate quality
- **THEN** it SHALL use deterministic counts and bounded reason categories rather than live-provider prose or repository-specific hard-coded candidate titles
