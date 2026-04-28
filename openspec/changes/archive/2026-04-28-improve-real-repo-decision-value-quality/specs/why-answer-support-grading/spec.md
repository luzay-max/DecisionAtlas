## ADDED Requirements

### Requirement: Why support guidance reflects accepted candidate quality
The imported why experience SHALL account for accepted candidate quality and same-thread evidence when guiding users after the first imported baseline is accepted.

#### Scenario: Strong accepted candidate improves bounded why guidance
- **WHEN** an accepted imported decision has strong grounding and a why question matches its rationale thread
- **THEN** the why experience SHALL be able to present that question as a supported downstream path

#### Scenario: Thin accepted candidate keeps why guidance cautious
- **WHEN** the first accepted imported decision has thin grounding or unclear provenance
- **THEN** the why experience SHALL avoid implying broad support and SHALL keep unrelated or weakly grounded questions evidence-limited or review-required

#### Scenario: Review quality cues explain why limitations
- **WHEN** a why answer remains limited after an accepted baseline exists
- **THEN** the product SHALL be able to connect that limitation to candidate/source-ref quality where applicable
