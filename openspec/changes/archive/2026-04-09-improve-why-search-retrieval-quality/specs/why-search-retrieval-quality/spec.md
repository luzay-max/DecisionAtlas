## ADDED Requirements

### Requirement: Why-search improves retrieval recall for equivalent questions
The system SHALL normalize technically equivalent why-questions and combine lexical and semantic retrieval strongly enough that equivalent user wording still finds the same accepted decision rationale.

#### Scenario: Equivalent phrasing still retrieves the same primary decision
- **WHEN** two why-questions use different but technically equivalent terminology for the same repository decision
- **THEN** the system SHALL still favor the same primary accepted decision instead of drifting to a neighboring but distinct decision

#### Scenario: Hybrid retrieval uses semantic support materially
- **WHEN** a why-question is phrased differently from the accepted decision text but remains semantically aligned
- **THEN** the system SHALL allow semantic retrieval to materially improve recall instead of depending almost entirely on exact wording

### Requirement: Why-search can use artifact chunks as supporting evidence
The system SHALL use artifact-chunk retrieval as a supporting evidence layer behind accepted decisions so imported why answers can assemble richer grounded support without replacing accepted decisions as the trust anchor.

#### Scenario: Accepted decision gains chunk-backed support
- **WHEN** a primary accepted decision is selected for a why-answer and relevant artifact chunks exist that support the same rationale thread
- **THEN** the system SHALL be able to use those chunks to strengthen the grounded evidence for that answer

#### Scenario: Chunk support does not replace accepted decision anchoring
- **WHEN** artifact chunks are retrieved as supporting evidence for a why-answer
- **THEN** the system SHALL keep the accepted decision as the answer anchor instead of answering directly from raw chunk evidence alone
