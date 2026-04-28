## ADDED Requirements

### Requirement: Imported review cards expose candidate quality cues
The review queue SHALL expose compact candidate quality cues so reviewers can judge imported decisions quickly without opening every detail page.

#### Scenario: Review card shows grounding strength
- **WHEN** an imported candidate has source references
- **THEN** the review card SHALL show whether the candidate appears strongly grounded, partially grounded, or thinly grounded using source-ref count and preview availability

#### Scenario: Review card shows provenance context
- **WHEN** an imported candidate has artifact provenance
- **THEN** the review card SHALL show compact provenance such as artifact type, artifact title, repository, and source URL when available

#### Scenario: Review card shows confidence context
- **WHEN** an imported candidate has confidence or extraction metadata
- **THEN** the review card SHALL expose that context without implying confidence alone is sufficient for acceptance

#### Scenario: Low-value candidates are visibly bounded
- **WHEN** an imported candidate lacks useful source refs, provenance, or decision-specific content
- **THEN** the review card SHALL clearly label that limitation so reviewers do not confuse it with a strong baseline candidate

### Requirement: Imported review milestone guides next action
The review experience SHALL make the path from strong candidate acceptance to bounded why/drift usage clear.

#### Scenario: Before first acceptance review explains milestone
- **WHEN** an imported workspace has candidates and no accepted imported decisions
- **THEN** the review experience SHALL explain that accepting a well-supported candidate establishes the first durable baseline

#### Scenario: After acceptance review points to bounded why and drift
- **WHEN** an imported candidate is accepted
- **THEN** the product SHALL point to why or drift entry points while preserving guidance that downstream trust depends on matching grounded evidence
