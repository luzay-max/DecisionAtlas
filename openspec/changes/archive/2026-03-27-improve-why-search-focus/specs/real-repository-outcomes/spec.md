## MODIFIED Requirements

### Requirement: Imported why-search preserves decision-grounded trust
The system SHALL treat imported why-answers as trustworthy only when they are grounded in accepted imported decisions with citations, SHALL prefer a single primary accepted decision when the question is specific, and SHALL otherwise fail with an actionable explanation.

#### Scenario: Imported why-answer is grounded in accepted decisions
- **WHEN** the user asks a why-question in an imported workspace that has accepted decisions and matching source references
- **THEN** the system SHALL answer using those accepted decisions, SHALL identify a primary accepted decision for the answer, and SHALL return citations with the answer

#### Scenario: Imported why-search lacks accepted grounding
- **WHEN** the user asks a why-question in an imported workspace that does not yet have accepted decision grounding for the question
- **THEN** the system SHALL return an explicit evidence-limited or review-required outcome instead of a weak freeform answer

#### Scenario: Imported why-answer keeps related but distinct decisions separate
- **WHEN** the user asks a focused why-question and retrieval also finds nearby but distinct accepted decisions
- **THEN** the system SHALL keep those distinct decisions out of the main answer unless they qualify as supporting context for the same rationale thread
