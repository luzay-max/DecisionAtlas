## MODIFIED Requirements

### Requirement: Source-ref coverage supports candidate quality labels
The system SHALL use source-reference coverage, previewable quote availability, artifact provenance, source URL availability, and confidence context to support deterministic candidate quality labels on imported review surfaces and real-repository validation reports.

#### Scenario: Multiple grounded refs indicate stronger support
- **WHEN** an imported candidate has multiple previewable grounded source refs plus artifact provenance
- **THEN** the review surface SHALL be able to label the candidate as stronger evidence than a candidate with only one or no refs

#### Scenario: Missing preview remains explicit
- **WHEN** source refs exist but no previewable quote is available
- **THEN** the review surface SHALL distinguish that state from both strong previewable support and completely missing support

#### Scenario: Source-ref diagnostics inform quality reports
- **WHEN** real-repo validation summarizes candidate quality
- **THEN** it SHALL be able to report whether thin candidate quality is driven by low source-ref coverage

#### Scenario: Confidence does not replace source-ref coverage
- **WHEN** an imported candidate has high confidence but lacks sufficient grounded source-ref coverage
- **THEN** source-ref diagnostics SHALL prevent the candidate quality label from implying strong support

#### Scenario: Provenance gaps remain visible
- **WHEN** source refs exist but artifact provenance or source URL context is missing
- **THEN** review and validation surfaces SHALL preserve that gap as a bounded quality reason rather than hiding it behind the source-ref count
