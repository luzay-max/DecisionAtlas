## MODIFIED Requirements

### Requirement: Why-search answers expose focused supporting context
The system SHALL present supporting accepted decisions separately from the main why-answer so users can tell which decision directly answers the question and which decisions only add adjacent context, and SHALL report whether the resulting answer is fully or only partially supported.

#### Scenario: Answer contains one primary decision and one support
- **WHEN** the why-answer uses a supporting accepted decision in addition to the primary one
- **THEN** the response SHALL distinguish the primary answer from supporting context instead of concatenating both decisions into one undifferentiated answer block

#### Scenario: Focused answer reports partial support explicitly
- **WHEN** the why-answer is correctly anchored on a primary accepted decision but its current citation support is incomplete
- **THEN** the response SHALL expose that partial-support state without broadening the answer into additional unrelated decisions
