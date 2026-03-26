## ADDED Requirements

### Requirement: Imported decision extraction uses a staged funnel
The system SHALL use a staged extraction funnel for imported workspaces so expensive full candidate extraction is only applied to artifacts that first appear likely to contain a real engineering decision.

#### Scenario: Screen artifact before full extraction
- **WHEN** an imported-workspace artifact enters the extraction shortlist
- **THEN** the system SHALL evaluate whether the artifact is decision-like before attempting full structured candidate extraction

#### Scenario: Skip full extraction for screened negative artifact
- **WHEN** an imported-workspace artifact does not pass the decision-likeness screen
- **THEN** the system SHALL skip full structured extraction for that artifact and continue the import job

### Requirement: Imported extraction prioritizes rationale-bearing evidence
The system SHALL prioritize rationale-bearing imported artifacts so the extraction shortlist favors evidence that is more likely to produce reviewable engineering decisions.

#### Scenario: Prefer rationale-heavy document classes
- **WHEN** the imported repository contains ADRs, RFCs, architecture docs, migration docs, rollout docs, or similar rationale-bearing documents
- **THEN** the extraction shortlist SHALL rank those artifacts ahead of lower-signal imported artifacts such as generic issues or short commits

#### Scenario: Limit low-value full extraction work
- **WHEN** the imported repository contains many low-signal artifacts
- **THEN** the extraction funnel SHALL reduce how many of those artifacts reach full structured extraction

### Requirement: Imported extraction uses reduced relevant context
The system SHALL build extraction requests from the most relevant sections of an artifact rather than relying only on large raw truncation windows.

#### Scenario: Long imported document contains localized rationale
- **WHEN** an imported artifact is much larger than the extraction payload budget
- **THEN** the system SHALL prefer the title, path, headings, and relevant rationale-bearing sections over a mostly raw document slice

#### Scenario: Smaller payload preserves extraction continuity
- **WHEN** the system prepares a full extraction request for an imported artifact
- **THEN** the request SHALL stay within a bounded payload size that reduces timeout risk while preserving the most decision-relevant context

### Requirement: Imported extraction exposes throughput telemetry
The system SHALL expose extraction funnel telemetry so operators and users can tell how much extraction work has been processed and how much remains during a live import.

#### Scenario: Running import reports extraction counts
- **WHEN** a live import is in the `extracting_decisions` stage
- **THEN** the job summary SHALL report processed extraction work, total extraction work, and candidate creation counts

#### Scenario: Running import reports extraction ETA
- **WHEN** a live import is in the `extracting_decisions` stage and at least some extraction work has completed
- **THEN** the job summary SHALL report enough timing information for the product to estimate remaining extraction time
