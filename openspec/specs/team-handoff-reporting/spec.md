# team-handoff-reporting Specification

## Purpose
Define bounded team/customer handoff reporting for DecisionAtlas self-hosted and small-team delivery.

## Requirements

### Requirement: Team handoff report generation
The system SHALL generate team handoff reports in both machine-readable JSON and operator-readable Markdown formats.

#### Scenario: Generate handoff report
- **WHEN** an operator runs handoff report generation with an output path and available source evidence
- **THEN** the system SHALL write JSON and Markdown reports that summarize workspace scope, repository sources, decisions, review/audit activity, drift posture, governance readiness, benchmark evidence, hosted readiness, and known limitations

#### Scenario: Missing evidence is explicit
- **WHEN** optional evidence such as benchmark comparison, hosted readiness, or readiness history is not provided
- **THEN** the report SHALL mark that evidence family as `not_provided`, `operator_guided`, `known_limitation`, `warning`, or `blocking` rather than converting it to pass

### Requirement: Handoff report protects sensitive data
The system SHALL exclude credentials and unnecessary private source material from generated handoff reports.

#### Scenario: Token fields are omitted
- **WHEN** repository source evidence includes credential references, token status, local paths, or provider metadata
- **THEN** the handoff report SHALL include provider, access mode, authorization status, and workspace identity without exposing raw tokens or secret values

#### Scenario: Raw private content is omitted
- **WHEN** imported repository evidence contains decision snippets, source references, or benchmark examples
- **THEN** the handoff report SHALL include bounded summaries and source references only, and SHALL NOT include raw private repository dumps

### Requirement: Handoff report is suitable for customer and operator review
The system SHALL structure the Markdown handoff report so a human can review delivery state without reading raw JSON.

#### Scenario: Markdown includes delivery sections
- **WHEN** a Markdown handoff report is generated
- **THEN** it SHALL include sections for summary, workspace/repository scope, decision quality, drift/governance status, review/audit activity, readiness evidence, benchmark evidence, limitations, and recommended next actions

#### Scenario: Browser rehearsal opens report
- **WHEN** a generated Markdown report is opened in a browser/operator rehearsal
- **THEN** the report SHALL render as readable text and expose the summary, evidence status, and limitations without requiring a running backend

### Requirement: Handoff report schema is deterministic
The system SHALL keep handoff report output deterministic enough for release evidence comparison.

#### Scenario: Stable ordering
- **WHEN** the same source evidence is used for repeated report generation
- **THEN** report sections, evidence families, status ordering, and representative item ordering SHALL remain stable

#### Scenario: Source metadata is recorded
- **WHEN** a handoff report is generated
- **THEN** the JSON report SHALL record report schema version, generated timestamp, commit or version label when provided, source evidence paths, and generator command metadata

### Requirement: Handoff reports disclose license and support boundary
Team handoff reports SHALL disclose license/support boundary evidence when provided.

#### Scenario: Boundary evidence is included
- **WHEN** handoff report generation receives license/support boundary evidence
- **THEN** the report SHALL summarize tier, support window, deployment scope, upgrade channel, and non-enforced runtime boundary without exposing secrets

#### Scenario: Boundary evidence is missing
- **WHEN** handoff report generation does not receive license/support boundary evidence
- **THEN** the report SHALL mark the license/support boundary section as not provided or operator-guided rather than omitting it

### Requirement: Handoff report references clean install rehearsal
Team handoff reports SHALL disclose clean install rehearsal evidence when provided.

#### Scenario: Clean install evidence is included
- **WHEN** handoff report generation receives clean install rehearsal evidence
- **THEN** the report SHALL summarize clean install status, package path, clean workspace path, evidence family statuses, blockers, limitations, and recommended next actions

#### Scenario: Clean install evidence is missing
- **WHEN** handoff report generation does not receive clean install rehearsal evidence
- **THEN** the report SHALL mark the clean install rehearsal section as `not_provided` or `operator_guided` rather than omitting it

### Requirement: Team handoff can feed Code Decision Audit reports
Team handoff reports SHALL be usable as source evidence for customer-readable Code Decision Audit reports.

#### Scenario: Handoff evidence is supplied
- **WHEN** a team handoff JSON path is provided to the Code Decision Audit report builder
- **THEN** the audit report MUST summarize handoff status, workspace/repository scope, and source evidence states

#### Scenario: Handoff evidence is omitted
- **WHEN** handoff evidence is not supplied
- **THEN** the audit report MUST preserve handoff evidence as `not_provided`

### Requirement: Handoff report references external install evidence
Team handoff reports SHALL disclose external or customer-controlled host install evidence when provided.

#### Scenario: External install evidence is included
- **WHEN** handoff report generation receives external install evidence
- **THEN** the report SHALL summarize external install status, host class, package identity, lane statuses, blockers, limitations, and recommended next actions

#### Scenario: External install evidence is missing
- **WHEN** handoff report generation does not receive external install evidence
- **THEN** the report SHALL mark customer-controlled host install evidence as `not_provided` or `operator_guided` rather than omitting the section

#### Scenario: External install evidence contains sensitive material
- **WHEN** external install evidence includes raw tokens, `.env` secrets, private source content, raw backup material, or unbounded customer logs
- **THEN** handoff report generation SHALL reject the evidence or preserve a `blocked` status without copying sensitive content into the report

### Requirement: Handoff report references real continuity rehearsal
Team handoff reports SHALL disclose real backup/restore/upgrade rehearsal evidence when provided.

#### Scenario: Real continuity evidence is included
- **WHEN** handoff report generation receives real continuity rehearsal evidence
- **THEN** the report SHALL summarize continuity status, scratch scope, restore validation status, post-upgrade status, rollback plan status, blockers, limitations, and recommended next actions

#### Scenario: Real continuity evidence is missing
- **WHEN** handoff report generation does not receive real continuity rehearsal evidence
- **THEN** the report SHALL mark tested continuity evidence as `not_provided` or `operator_guided` rather than omitting the section

#### Scenario: Real continuity evidence contains sensitive material
- **WHEN** real continuity evidence includes raw backups, `.env` secrets, credential material, private source content, or unbounded local logs
- **THEN** handoff report generation SHALL reject the evidence or preserve a `blocking` status without copying sensitive content into the report
