## MODIFIED Requirements

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, SHALL distinguish partially supported answers from truly insufficient evidence, SHALL improve retrieval quality for technically equivalent questions, SHALL use artifact evidence only as a support layer behind the accepted decision anchor, SHALL expose bounded follow-up guidance when an imported workspace has an accepted baseline but the asked why-question is still weakly grounded, and SHALL make retrieval failures diagnosable enough for real-repository validation to classify them.

#### Scenario: Imported why-answer is grounded in accepted decisions
- **WHEN** the user asks a why-question in an imported workspace that has accepted decisions and matching source references
- **THEN** the system SHALL answer using those accepted decisions, SHALL identify a primary accepted decision for the answer, and SHALL return citations with the answer

#### Scenario: Imported why-answer has limited support
- **WHEN** the user asks a why-question in an imported workspace, the system selects a primary accepted decision, and only partial but still grounded citation support is available
- **THEN** the system SHALL return an explicit `limited_support` outcome instead of mislabeling the result as fully supported or as completely insufficient

#### Scenario: Truly weak or missing grounding still fails closed after first acceptance
- **WHEN** the user asks a why-question in an imported workspace that has accepted at least one decision but does not yet have enough grounding for the asked rationale thread
- **THEN** the system SHALL continue to return an explicit evidence-limited or review-required outcome instead of upgrading the result solely because the workspace has an accepted baseline

#### Scenario: Imported why-answer keeps related but distinct decisions separate
- **WHEN** the user asks a focused why-question and retrieval also finds nearby but distinct accepted decisions
- **THEN** the system SHALL keep those distinct decisions out of the main answer unless they qualify as supporting context for the same rationale thread

#### Scenario: Imported why-answer can use supporting artifact evidence
- **WHEN** the system finds relevant artifact evidence that supports the already selected primary accepted decision
- **THEN** the imported why experience SHALL use that evidence to strengthen the answer without replacing the primary accepted decision as the answer anchor

#### Scenario: Structured chunk evidence improves imported why support
- **WHEN** improved indexing produces chunk evidence with stronger section context for the same accepted decision rationale thread
- **THEN** the imported why experience SHALL be able to use that structured chunk evidence to improve support quality without changing the accepted decision that anchors the answer

#### Scenario: Accepted baseline with weak why grounding exposes bounded follow-up
- **WHEN** an imported workspace already has an accepted baseline but the asked why-question remains evidence-limited
- **THEN** the response SHALL keep that outcome bounded and SHALL expose follow-up guidance such as reviewing additional candidates or inspecting import evidence instead of implying the baseline alone solved the question

#### Scenario: Equivalent why question records retrieval usefulness
- **WHEN** a real-repository validation why case uses equivalent wording for an accepted imported decision
- **THEN** validation output SHALL be able to record whether the answer selected the expected primary rationale thread and returned the expected bounded support state

### Requirement: Real repository outcomes report decision-value quality
The system SHALL evaluate imported real-repository outcomes not only by readiness state, but also by whether reviewable candidate decisions are valuable, grounded, and useful for establishing the first accepted baseline, using the same candidate quality labels and reason categories exposed in the review product, and SHALL include imported why-search retrieval usefulness when accepted baselines are available.

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

#### Scenario: Why retrieval quality is recorded after first baseline
- **WHEN** a curated imported repository has an accepted baseline and real-repository why cases
- **THEN** validation output SHALL record expected status, observed status, citation count, expected term matches, and primary-thread match evidence where available
