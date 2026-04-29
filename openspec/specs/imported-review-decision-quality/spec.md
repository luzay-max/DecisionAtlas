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

### Requirement: Imported review cards expose candidate quality cues
The review queue SHALL expose compact candidate quality cues so reviewers can judge imported decisions quickly without opening every detail page, and those cues SHALL explain the evidence boundary that caused a candidate to be labeled `strong`, `partial`, or `thin`.

#### Scenario: Review card shows grounding strength
- **WHEN** an imported candidate has source references
- **THEN** the review card SHALL show whether the candidate appears strongly grounded, partially grounded, or thinly grounded using source-ref count, preview availability, and provenance availability

#### Scenario: Review card shows provenance context
- **WHEN** an imported candidate has artifact provenance
- **THEN** the review card SHALL show compact provenance such as artifact type, artifact title, repository, and source URL when available

#### Scenario: Review card shows confidence context
- **WHEN** an imported candidate has confidence or extraction metadata
- **THEN** the review card SHALL expose that context without implying confidence alone is sufficient for acceptance or for a `strong` quality label

#### Scenario: Low-value candidates are visibly bounded
- **WHEN** an imported candidate lacks useful source refs, provenance, or decision-specific content
- **THEN** the review card SHALL clearly label that limitation so reviewers do not confuse it with a strong baseline candidate

#### Scenario: Partial candidates explain missing support
- **WHEN** an imported candidate has some grounded support but does not satisfy the strong candidate boundary
- **THEN** the review card SHALL identify it as partial and expose the missing or limited support category such as single source ref, missing previewable quote, missing source URL, or missing artifact provenance

#### Scenario: Strong candidates require evidence and provenance
- **WHEN** an imported candidate has high confidence but lacks grounded source refs, previewable quotes, or artifact provenance
- **THEN** the review card SHALL NOT label that candidate as strong

### Requirement: Imported review milestone guides next action
The review experience SHALL make the path from strong candidate acceptance to bounded why/drift usage clear.

#### Scenario: Before first acceptance review explains milestone
- **WHEN** an imported workspace has candidates and no accepted imported decisions
- **THEN** the review experience SHALL explain that accepting a well-supported candidate establishes the first durable baseline

#### Scenario: After acceptance review points to bounded why and drift
- **WHEN** an imported candidate is accepted
- **THEN** the product SHALL point to why or drift entry points while preserving guidance that downstream trust depends on matching grounded evidence
