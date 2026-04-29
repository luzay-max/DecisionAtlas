## MODIFIED Requirements

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
