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

### Requirement: Decision review history is visible
The decision review experience SHALL expose bounded review history for imported and demo decisions without changing the existing accept, reject, supersede, and candidate actions.

#### Scenario: Decision detail shows review history
- **WHEN** a viewer opens a decision that has review audit events
- **THEN** the detail view SHALL show the recent review history including actor, action, previous review state, new review state, rationale when present, and timestamp

#### Scenario: Review action response includes audit event
- **WHEN** a reviewer changes a decision review state
- **THEN** the review response SHALL include or make available the resulting audit event so product surfaces can update without a page reload

#### Scenario: Review queue remains simple
- **WHEN** a reviewer evaluates imported candidate decisions from the review queue
- **THEN** the product SHALL preserve the existing simple candidate action flow while making recent review history available on the detail page or compact card context

### Requirement: Imported review queues explain precision ranking and duplicate context
The imported review experience SHALL expose the canonical precision tier, ranking reasons, extraction origin, and near-duplicate context needed to understand queue order without presenting the ranking as an approval decision.

#### Scenario: Queue summarizes precision tiers
- **WHEN** an imported review queue contains candidate decisions
- **THEN** the page SHALL summarize the number of strong, partial, weak, and secondary duplicate candidates

#### Scenario: Review card explains queue position
- **WHEN** an imported candidate has a precision profile
- **THEN** its review card SHALL show its tier and bounded reasons including extraction origin when known

#### Scenario: Duplicate member points to representative
- **WHEN** an imported candidate is a secondary member of a near-duplicate cluster
- **THEN** its review card SHALL identify the cluster size and link to or name the representative candidate

#### Scenario: Weak candidates remain visible
- **WHEN** a candidate is weak or a secondary duplicate
- **THEN** it SHALL remain individually visible and reviewable rather than being automatically hidden or rejected

#### Scenario: Ranking does not imply acceptance
- **WHEN** a candidate is classified strong or ranked first
- **THEN** the review experience SHALL still require an explicit human review action before it becomes accepted
