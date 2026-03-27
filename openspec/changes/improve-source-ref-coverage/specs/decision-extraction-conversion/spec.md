## MODIFIED Requirements

### Requirement: Full extraction can salvage decision-like structured output
The system SHALL distinguish between true non-decision outputs and recoverable partial extraction outputs so screened-in artifacts are not discarded solely because the first structured response is imperfect, and SHALL preserve enough grounded evidence from valid outputs to avoid leaving those decisions under-supported downstream.

#### Scenario: Core decision fields are present
- **WHEN** the full extraction response contains enough core decision fields and grounded evidence to describe a reviewable engineering decision
- **THEN** the system SHALL normalize and persist a candidate decision even if optional fields or formatting details are incomplete

#### Scenario: Response lacks sufficient decision structure
- **WHEN** the full extraction response does not contain enough grounded decision structure to create a trustworthy candidate
- **THEN** the system SHALL skip candidate creation and record a conversion-loss reason instead of persisting a weak candidate

#### Scenario: Valid decision still has thin grounded support
- **WHEN** the extraction response is good enough to create a decision but grounding only yields a single retained source ref from evidence that should support more
- **THEN** the system SHALL classify that outcome separately from general extraction failure so conversion diagnostics can identify source-ref coverage limits
