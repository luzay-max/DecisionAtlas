# private-repo-pilot-evidence Specification

## Purpose
Define safe, customer-controlled evidence collection for private repository pilot validations without committing private source content, credentials, or customer identifiers.

## Requirements

### Requirement: Private-repo pilot evidence template is customer-safe
The system SHALL provide a private-repository pilot evidence template that records pilot proof without requiring raw private source content, raw issue or pull-request text, token material, provider keys, or customer-identifying details in committed artifacts.

#### Scenario: Operator prepares private-repo evidence
- **WHEN** an operator prepares private-repository pilot evidence for a customer-controlled run
- **THEN** the template SHALL include repository identity handling, credential custody, import outcome, review outcome, why-search outcome, drift outcome, generated evidence references, limitations, and recommended next actions
- **AND** it SHALL require redacted or category-level fields instead of raw private source content, raw issue or pull-request text, token values, provider keys, or customer identifiers.

#### Scenario: Private proof is not available
- **WHEN** no real private-repository run has been completed or no shareable redacted evidence has been approved
- **THEN** the evidence SHALL preserve `operator_guided` or `not_provided` status rather than claiming a clean pass.

### Requirement: Private-repo pilot evidence verifier preserves safety boundaries
The system SHALL provide a local verifier that validates private-repo pilot evidence files for required structure, required safety statements, required workflow lanes, and obvious forbidden sensitive material.

#### Scenario: Safe sample evidence is verified
- **WHEN** the verifier receives JSON and Markdown private-repo pilot evidence that includes required redaction, token custody, source-content exclusion, and operator-review statements
- **THEN** it SHALL emit machine-readable and Markdown verification evidence with status `pass` or `operator_guided` and checked items.

#### Scenario: Unsafe evidence is detected
- **WHEN** evidence includes obvious token-like values, raw secret markers, missing redaction statements, missing credential custody statements, or missing private-source exclusion statements
- **THEN** the verifier SHALL emit status `blocking` and identify the failed checks without echoing sensitive values.

### Requirement: Private-repo evidence integrates with delivery evidence
The system SHALL make private-repo pilot evidence usable from pilot delivery, self-hosted commercial, handoff, and audit-report workflows as bounded input evidence.

#### Scenario: Pilot delivery references private-repo proof
- **WHEN** a pilot claim says that DecisionAtlas has been validated against a private repository
- **THEN** the delivery materials SHALL reference sanitized private-repo pilot evidence or explicitly disclose that the private-repo evidence is missing or operator-guided.

#### Scenario: Evidence enters customer handoff
- **WHEN** a maintainer or operator prepares customer handoff or Code Decision Audit material from private-repo pilot evidence
- **THEN** the handoff SHALL preserve warning, blocking, operator-guided, known-limitation, and not-provided states instead of converting them to pass.
