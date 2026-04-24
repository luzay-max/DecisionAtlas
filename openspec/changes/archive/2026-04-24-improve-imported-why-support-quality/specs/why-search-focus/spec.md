## MODIFIED Requirements

### Requirement: Why-search selects a primary accepted decision
The system SHALL select one primary accepted decision for a why-answer before deciding whether any secondary decision may be included as supporting context, and SHALL keep focused imported why questions anchored to the accepted decision that best matches the asked rationale thread instead of whichever nearby decision happened to rank first lexically.

#### Scenario: Single-decision question maps to one primary answer
- **WHEN** a why-question clearly aligns to one accepted decision
- **THEN** the system SHALL anchor the answer on that primary accepted decision instead of blending multiple adjacent decisions into the main answer body

#### Scenario: Secondary decision requires support eligibility
- **WHEN** another accepted decision is also retrieved for the same why-question
- **THEN** the system SHALL include it only if it materially supports the same rationale thread as the primary accepted decision

#### Scenario: Focused imported question rejects weaker neighboring decision
- **WHEN** a focused imported why-question retrieves multiple accepted decisions and the highest raw hit is a weaker neighboring match than another candidate
- **THEN** the system SHALL prefer the accepted decision with the stronger rationale-thread fit as the primary answer

### Requirement: Why-search uses stronger query normalization
The system SHALL normalize technically equivalent why-questions so wording differences do not unnecessarily push retrieval toward a neighboring but distinct accepted decision, and that normalization SHALL include technical aliases and equivalent repository-specific phrasing while preserving question intent and decision specificity.

#### Scenario: Synonym-like question retrieves the same accepted decision
- **WHEN** two why-questions use different but technically equivalent phrasing for the same concept
- **THEN** the system SHALL normalize them so retrieval still favors the same primary accepted decision

#### Scenario: Query normalization preserves decision intent
- **WHEN** the system rewrites a why-question before retrieval
- **THEN** it SHALL preserve the intent of the question and SHALL NOT broaden it into a generic topic query

#### Scenario: Technical alias does not broaden focused imported question
- **WHEN** an imported why-question uses a repository-specific alias or technically equivalent term
- **THEN** the normalization path SHALL preserve the focused decision intent instead of broadening the question into a looser topic search

### Requirement: Why-search answers expose focused supporting context
The system SHALL present supporting accepted decisions separately from the main why-answer so users can tell which decision directly answers the question and which decisions only add adjacent context, SHALL report whether the resulting answer is fully or only partially supported, and SHALL allow retrieval-backed supporting evidence to strengthen the primary answer without broadening it into unrelated decision context.

#### Scenario: Answer contains one primary decision and one support
- **WHEN** the why-answer uses a supporting accepted decision in addition to the primary one
- **THEN** the response SHALL distinguish the primary answer from supporting context instead of concatenating both decisions into one undifferentiated answer block

#### Scenario: Focused answer reports partial support explicitly
- **WHEN** the why-answer is correctly anchored on a primary accepted decision but its current citation support is incomplete
- **THEN** the response SHALL expose that partial-support state without broadening the answer into additional unrelated decisions

#### Scenario: Focused imported answer omits unrelated supporting context
- **WHEN** a focused imported why-question retrieves nearby accepted decisions that do not materially support the same rationale thread
- **THEN** the response SHALL omit those decisions from supporting context rather than using them to make the answer look stronger
