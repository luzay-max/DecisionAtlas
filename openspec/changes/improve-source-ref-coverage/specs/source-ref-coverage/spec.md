## ADDED Requirements

### Requirement: Extracted decisions retain multiple grounded source refs when available
The system SHALL retain more than one grounded source reference for an extracted decision when the underlying imported artifact contains multiple decision-supporting quotes that can be mapped back to real spans.

#### Scenario: One artifact contains multiple grounded decision quotes
- **WHEN** full extraction identifies a valid decision from an imported artifact and that artifact contains more than one quote supporting the decision
- **THEN** the system SHALL persist multiple grounded source references for that decision instead of stopping after the first successful ref

#### Scenario: Additional quote cannot be grounded
- **WHEN** an additional candidate quote cannot be mapped back to a concrete artifact span
- **THEN** the system SHALL skip that quote rather than persisting an ungrounded source reference

### Requirement: Thin source-ref coverage is diagnosable
The system SHALL distinguish valid extracted decisions with thin grounded support from broader extraction failure so operators can understand why many imported why-answers remain partially supported.

#### Scenario: Decision is created with only one grounded ref
- **WHEN** a decision is created successfully but only one grounded source reference can be retained
- **THEN** the system SHALL record that thin-coverage outcome in machine-readable diagnostics

#### Scenario: Validation can inspect thin-coverage pressure
- **WHEN** imported why-quality validation runs against a workspace or benchmark fixture set
- **THEN** the system SHALL expose enough data to tell whether partially supported answers are driven by thin source-ref coverage
