## MODIFIED Requirements

### Requirement: Why-search uses stronger query normalization
The system SHALL normalize technically equivalent why-questions so wording differences do not unnecessarily push retrieval toward a neighboring but distinct accepted decision, and that normalization SHALL include technical aliases and equivalent repository-specific phrasing while preserving question intent.

#### Scenario: Synonym-like question retrieves the same accepted decision
- **WHEN** two why-questions use different but technically equivalent phrasing for the same concept
- **THEN** the system SHALL normalize them so retrieval still favors the same primary accepted decision

#### Scenario: Query normalization preserves decision intent
- **WHEN** the system rewrites a why-question before retrieval
- **THEN** it SHALL preserve the intent of the question and SHALL NOT broaden it into a generic topic query

### Requirement: Why-search answers expose focused supporting context
The system SHALL present supporting accepted decisions separately from the main why-answer so users can tell which decision directly answers the question and which decisions only add adjacent context, SHALL report whether the resulting answer is fully or only partially supported, and SHALL allow retrieval-backed supporting evidence to strengthen the primary answer without broadening it into unrelated decision context.

#### Scenario: Answer contains one primary decision and one support
- **WHEN** the why-answer uses a supporting accepted decision in addition to the primary one
- **THEN** the response SHALL distinguish the primary answer from supporting context instead of concatenating both decisions into one undifferentiated answer block

#### Scenario: Focused answer reports partial support explicitly
- **WHEN** the why-answer is correctly anchored on a primary accepted decision but its current citation support is incomplete
- **THEN** the response SHALL expose that partial-support state without broadening the answer into additional unrelated decisions
