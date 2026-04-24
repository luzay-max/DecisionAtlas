## MODIFIED Requirements

### Requirement: First accepted imported baseline is treated as a product milestone
The system SHALL treat the first accepted imported decision as the first durable product milestone after candidate review, SHALL make the review path to that milestone clear when imported candidates are available, and SHALL use that milestone to upgrade imported workflow guidance without implying that all downstream questions are now fully supported.

#### Scenario: First accepted milestone changes imported next-step messaging
- **WHEN** an imported workspace transitions from zero accepted decisions to one accepted decision
- **THEN** the product SHALL be able to explain that the workspace now has a durable baseline and can support grounded why usage for matching questions

#### Scenario: Review queue explains milestone before first acceptance
- **WHEN** an imported workspace has reviewable candidate decisions and no accepted imported decision
- **THEN** the review experience SHALL explain that accepting a well-supported candidate establishes the first baseline for downstream why/drift usage

#### Scenario: Review acceptance does not overstate downstream trust
- **WHEN** the first imported candidate is accepted
- **THEN** downstream guidance SHALL still distinguish grounded matching why questions from unrelated questions that remain review-required or evidence-limited
