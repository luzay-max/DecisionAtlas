## ADDED Requirements

### Requirement: Source-ref coverage supports candidate quality labels
The system SHALL use source-reference coverage to support candidate quality labels on imported review surfaces.

#### Scenario: Multiple grounded refs indicate stronger support
- **WHEN** an imported candidate has multiple previewable grounded source refs
- **THEN** the review surface SHALL be able to label the candidate as stronger evidence than a candidate with only one or no refs

#### Scenario: Missing preview remains explicit
- **WHEN** source refs exist but no previewable quote is available
- **THEN** the review surface SHALL distinguish that state from both strong previewable support and completely missing support

#### Scenario: Source-ref diagnostics inform quality reports
- **WHEN** real-repo validation summarizes candidate quality
- **THEN** it SHALL be able to report whether thin candidate quality is driven by low source-ref coverage
