## ADDED Requirements

### Requirement: Candidate precision profiles are evidence-first and deterministic
The system SHALL calculate a bounded precision profile for each imported candidate using grounded source coverage, previewable evidence, artifact provenance, confidence, decision specificity, artifact family, and extraction-origin metadata, and SHALL return the same profile for unchanged inputs.

#### Scenario: Grounded candidate ranks above confidence-only candidate
- **WHEN** two candidates have comparable confidence but one has stronger grounded evidence and provenance
- **THEN** the grounded candidate SHALL receive the higher precision score and queue position

#### Scenario: Confidence alone cannot create strong tier
- **WHEN** a candidate has high confidence but lacks grounded source refs or artifact provenance
- **THEN** the system SHALL NOT classify the candidate in the strong precision tier

#### Scenario: Legacy extraction metadata remains usable
- **WHEN** an existing candidate has no per-candidate extraction metadata
- **THEN** the system SHALL identify extraction origin as unknown without assuming the candidate was salvaged or recovered

#### Scenario: Ranking reasons are bounded
- **WHEN** a precision profile is returned
- **THEN** its reasons SHALL use stable machine-readable categories and SHALL NOT contain raw provider output

### Requirement: Near-duplicate candidates are clustered without data loss
The system SHALL identify conservative near-duplicate candidate clusters within one workspace, choose the strongest representative deterministically, and preserve every candidate for individual review and audit.

#### Scenario: Similar decision candidates form one cluster
- **WHEN** candidates have sufficiently overlapping decision-bearing title, problem, chosen-option, and tradeoff content
- **THEN** the system SHALL assign them one stable cluster and expose one highest-ranked representative

#### Scenario: Generic overlap does not force a cluster
- **WHEN** candidates share only generic engineering words but describe different choices
- **THEN** the system SHALL keep them in separate clusters

#### Scenario: Secondary duplicate remains reviewable
- **WHEN** a candidate is a non-representative member of a near-duplicate cluster
- **THEN** the API SHALL expose its representative reference and SHALL NOT delete, merge, accept, or reject it automatically

#### Scenario: Cluster order is stable
- **WHEN** the same unchanged candidate set is requested repeatedly
- **THEN** cluster identifiers, representatives, scores, tiers, and queue ordering SHALL remain stable

### Requirement: Candidate review queues use canonical precision ordering
The system SHALL order imported candidate review queues by canonical precision tier, representative status, score, and stable tie-breakers while preserving existing ordering semantics for non-candidate decision lists.

#### Scenario: Strong representative appears before weak duplicate
- **WHEN** a queue contains a strong cluster representative and a weak or secondary duplicate candidate
- **THEN** the strong representative SHALL appear first

#### Scenario: Equal profiles use stable tie-breakers
- **WHEN** candidates have equal tier and precision score
- **THEN** the system SHALL use deterministic creation and identifier tie-breakers

#### Scenario: Non-candidate list remains compatible
- **WHEN** accepted, rejected, superseded, or unfiltered non-candidate decisions are listed
- **THEN** the system SHALL preserve the established non-candidate ordering and response compatibility
