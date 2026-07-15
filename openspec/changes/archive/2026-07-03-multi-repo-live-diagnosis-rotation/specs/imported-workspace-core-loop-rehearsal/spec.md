## ADDED Requirements

### Requirement: Core-loop evidence can be aggregated
Imported workspace core-loop evidence SHALL be usable as an input to multi-repo diagnosis.

#### Scenario: Multi-repo diagnosis runs
- **WHEN** a repository has a workspace slug from explicit metadata, lookup, or public import rehearsal
- **THEN** core-loop evidence SHALL be collected for that repository and summarized without embedding raw private content.

#### Scenario: Core-loop evidence is warning
- **WHEN** core-loop evidence for a repository is warning or blocking
- **THEN** multi-repo diagnosis SHALL preserve that repository status and include recommended follow-up.
