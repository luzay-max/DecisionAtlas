## MODIFIED Requirements

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, SHALL distinguish partially supported answers from truly insufficient evidence, SHALL improve retrieval quality for technically equivalent questions, SHALL use artifact evidence only as a support layer behind the accepted decision anchor, and SHALL expose bounded follow-up guidance when an imported workspace has an accepted baseline but the asked why-question is still weakly grounded.

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
