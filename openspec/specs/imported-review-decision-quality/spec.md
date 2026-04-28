## Purpose
Define decision-quality expectations for imported review cards and review workflows.

## Requirements

### Requirement: Imported review cards expose enough evidence to judge candidates
The system SHALL make imported candidate decisions reviewable from the review queue by showing compact evidence, provenance, and confidence context without requiring reviewers to open every decision detail page.

#### Scenario: Imported candidate shows evidence preview
- **WHEN** an imported candidate decision has grounded source refs
- **THEN** the review queue SHALL show a compact preview of at least one supporting quote and the total grounded source-ref count

#### Scenario: Imported candidate shows provenance
- **WHEN** an imported candidate decision is backed by a source artifact
- **THEN** the review queue SHALL show compact artifact provenance such as source type, title, repository, and URL when available

#### Scenario: Thin evidence is visible
- **WHEN** an imported candidate has only thin source-ref coverage or no previewable source refs
- **THEN** the review queue SHALL clearly indicate limited review evidence instead of implying the candidate is fully grounded

#### Scenario: Review detail remains available
- **WHEN** a reviewer needs the full candidate context
- **THEN** the review queue SHALL still link to the decision detail page with full source refs

### Requirement: Imported review guidance explains first accepted baseline
The system SHALL explain that accepting a strong imported candidate establishes the first durable imported baseline used by downstream why-search and drift, while avoiding claims that every downstream question becomes supported automatically.

#### Scenario: Imported review-ready workspace shows baseline guidance
- **WHEN** an imported workspace has candidate decisions but no accepted imported decisions
- **THEN** the review page SHALL explain that reviewers should accept the first well-supported candidate to establish a durable baseline

#### Scenario: Candidate actions remain simple
- **WHEN** a reviewer evaluates an imported candidate
- **THEN** the product SHALL keep the existing accept, reject, and supersede actions rather than introducing a separate approval workflow

#### Scenario: Accepted candidate routes downstream
- **WHEN** an imported candidate is accepted from the review queue
- **THEN** the product SHALL make the next downstream why or drift entry point clear without claiming broad trust beyond grounded matching questions
