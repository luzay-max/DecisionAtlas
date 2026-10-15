## Purpose
Define precise, deterministic, explainable canonicalization of governance drift findings while preserving distinct issues, bounded evidence, recurrence metadata, and advisory behavior.

## Requirements

### Requirement: Repeated-issue candidates are precise
The system SHALL recognize repeated historical issues using bounded issue markers and substantial semantic overlap with recent context, and SHALL reject incidental substrings, policy mentions, and negated successful outcomes.

#### Scenario: Ordinary text contains an issue substring
- **WHEN** a governance source contains words such as decisions or describes private issue text handling without reporting an incident
- **THEN** the detector SHALL NOT create a repeated_postmortem_issue signal from that text

#### Scenario: Successful outcome negates a failure marker
- **WHEN** a source states that no runtime errors occurred or that an outcome is not a runtime failure
- **THEN** the detector SHALL NOT treat the statement as a historical issue

#### Scenario: Historical issue substantially overlaps recent context
- **WHEN** an explicit or strong historical failure statement has at least three meaningful overlapping tokens and substantial token coverage against recent context
- **THEN** the detector SHALL retain it as a repeated-issue candidate for canonical grouping
### Requirement: Equivalent governance findings have one canonical representation
The system SHALL group governance drift signals that represent the same actionable issue by a deterministic, type-aware semantic identity before report status and downstream summaries are computed.

#### Scenario: Repeated issue wording from multiple sources is consolidated
- **WHEN** multiple postmortem, update-log, or archived-change sources describe the same repeated issue with only path, punctuation, whitespace, counter, or timestamp variation
- **THEN** the detector SHALL return one canonical `repeated_postmortem_issue` signal for that actionable issue

#### Scenario: Distinct issues remain separate
- **WHEN** two signals share a type or generic title but describe different actionable issues
- **THEN** the detector SHALL preserve them as separate canonical signals

### Requirement: Canonical findings preserve bounded recurrence evidence
The system SHALL merge unique evidence for grouped findings, SHALL expose total occurrence and unique-source counts, and SHALL bound serialized evidence deterministically.

#### Scenario: Duplicate evidence is not repeated
- **WHEN** equivalent signals reference the same evidence identity more than once
- **THEN** the canonical finding SHALL include that evidence once while preserving the full occurrence count

#### Scenario: Evidence exceeds the serialization bound
- **WHEN** a canonical finding contains more unique evidence references than the configured bound
- **THEN** the detector SHALL return a deterministic bounded evidence list and SHALL retain source and occurrence counts that describe the complete group

### Requirement: Deduplicated output is stable and explainable
The system SHALL produce the same canonical IDs, ordering, representative wording, counts, and bounded evidence for equivalent input regardless of source discovery order.

#### Scenario: Input order changes
- **WHEN** equivalent source inputs are supplied in a different order
- **THEN** the serialized canonical findings SHALL remain identical

#### Scenario: Operator views a recurring finding
- **WHEN** a dashboard or machine consumer receives a canonical finding with more than one occurrence
- **THEN** the result SHALL expose recurrence metadata that distinguishes a recurring pattern from a single occurrence

### Requirement: Deduplication remains advisory
The system SHALL NOT acknowledge, resolve, suppress, or mutate governance sources as a side effect of canonicalizing drift findings.

#### Scenario: Equivalent findings are grouped
- **WHEN** the detector consolidates equivalent signals
- **THEN** source artifacts and persisted review or disposition state SHALL remain unchanged
