# code-decision-audit-report-builder Specification

## Purpose
Define customer-readable Code Decision Audit report generation from bounded DecisionAtlas release, readiness, benchmark, handoff, and commercial-fit evidence.

## Requirements

### Requirement: Audit report builder generates customer-readable artifacts
The system SHALL provide a local Code Decision Audit report builder that writes JSON and Markdown from explicit evidence inputs.

#### Scenario: Evidence inputs are supplied
- **WHEN** release evidence, hosted readiness, benchmark trend, coverage rehearsal, team handoff, readiness history, or license/support evidence JSON paths are supplied
- **THEN** the builder MUST summarize those sources in customer-readable JSON and Markdown

#### Scenario: Evidence input is omitted
- **WHEN** an optional evidence source is not supplied
- **THEN** the builder MUST record that source as `not_provided` instead of searching `.tmp` implicitly

### Requirement: Audit report preserves non-clean states
The audit report SHALL preserve non-clean evidence states.

#### Scenario: Source evidence contains warning states
- **WHEN** source evidence includes `warning`, `operator_guided`, `known_limitation`, `not_provided`, or `blocking`
- **THEN** the audit report MUST show those states and recommend follow-up rather than summarizing the report as clean

### Requirement: Audit report is customer-safe
The audit report SHALL avoid exposing secrets, raw private repository content, raw model output, or unbounded local paths.

#### Scenario: Report is shared with a pilot customer
- **WHEN** the generated Markdown is shared externally
- **THEN** it MUST contain bounded statuses, source artifact names, counts, limitations, commercial fit, and next actions

### Requirement: Audit report includes commercial fit
The audit report SHALL map the evidence to Community, Team Self-hosted, or Enterprise Self-hosted fit.

#### Scenario: Tier is supplied
- **WHEN** the operator supplies a recommended tier
- **THEN** the report MUST include the tier, rationale, and open commercial questions

### Requirement: Audit report references external install readiness
Code Decision Audit reports SHALL reference external self-hosted install evidence when sanitized evidence is provided.

#### Scenario: External install evidence is supplied
- **WHEN** the Code Decision Audit report builder receives external install evidence
- **THEN** the audit report MUST summarize external install status, host class, package identity, checked lanes, limitations, and customer-readiness implications

#### Scenario: External install evidence is omitted
- **WHEN** external install evidence is not supplied
- **THEN** the audit report MUST preserve external install evidence as `not_provided` or `operator_guided` and MUST NOT claim customer-controlled host validation

#### Scenario: External install evidence is unsafe
- **WHEN** supplied external install evidence contains sensitive material or blocked redaction status
- **THEN** the audit report builder MUST reject the evidence or include only a bounded blocked summary without exposing sensitive content
