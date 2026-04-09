## ADDED Requirements

### Requirement: Artifact indexing preserves document structure for evidence retrieval
The system SHALL chunk repository artifacts in a structure-aware way so rationale-bearing sections are preserved more faithfully than with flat paragraph splitting alone.

#### Scenario: Heading-bearing document is chunked by section
- **WHEN** an imported repository document contains markdown-style or document-style section boundaries
- **THEN** the indexing path SHALL prefer section-aware chunk boundaries before falling back to coarse fixed slicing

#### Scenario: Oversized section uses bounded fallback subdivision
- **WHEN** a single structured section still exceeds the chunk size target
- **THEN** the indexing path SHALL subdivide that section in bounded slices instead of discarding the section boundary entirely

### Requirement: Artifact chunks preserve limited overlap across split boundaries
The system SHALL preserve bounded overlap when a chunk must be split from a larger section so evidence retrieval does not lose cross-boundary meaning.

#### Scenario: Cross-boundary rationale survives chunk split
- **WHEN** important rationale text spans the end of one chunk and the beginning of the next
- **THEN** the indexed chunk set SHALL retain enough overlap that retrieval can still recover the rationale thread

### Requirement: Artifact chunks store structural metadata for later ranking
The system SHALL store structural metadata with artifact chunks so retrieval and explanation layers can distinguish richer rationale-bearing evidence from generic body text.

#### Scenario: Stored chunk metadata captures section context
- **WHEN** an artifact chunk is written during indexing
- **THEN** the stored row SHALL retain structural context such as heading path, section label, or chunk role alongside the chunk content

#### Scenario: Retrieval remains compatible while metadata coverage is mixed
- **WHEN** retrieval runs against a workspace whose chunks do not all have the new metadata yet
- **THEN** the system SHALL remain functional and treat missing metadata as weaker context rather than as a failure
