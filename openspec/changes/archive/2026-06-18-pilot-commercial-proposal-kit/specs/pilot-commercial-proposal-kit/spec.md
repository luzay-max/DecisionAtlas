## ADDED Requirements

### Requirement: Pilot commercial proposal kit is customer-ready
The system SHALL provide a pilot commercial proposal kit that explains the paid pilot offer, scope, assumptions, acceptance criteria, support boundary, and renewal or upgrade path without requiring a billing system.

#### Scenario: Customer reviews paid pilot proposal
- **WHEN** a customer or operator opens the proposal kit
- **THEN** it SHALL include proposal summary, target buyer, pilot scope, pilot duration, draft price assumptions, deliverables, acceptance criteria, evidence requirements, support boundary, and next-step decision options.

#### Scenario: Deferred commercial capabilities are disclosed
- **WHEN** the proposal kit describes current product capabilities
- **THEN** it SHALL disclose that billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, online license server, and runtime license enforcement are not part of the current self-hosted pilot package.

### Requirement: Pilot commercial proposal kit preserves evidence boundaries
The proposal kit SHALL require paid pilot claims to reference generated evidence or preserve warning, operator-guided, known-limitation, not-provided, or blocking states.

#### Scenario: Paid pilot acceptance criteria are prepared
- **WHEN** an operator prepares pilot acceptance criteria
- **THEN** the criteria SHALL reference package verification, clean install rehearsal, release evidence, hosted/operator readiness, readiness history, real-repo benchmark evidence, private-repo pilot evidence when applicable, and backup/restore/upgrade rehearsal evidence.

#### Scenario: Evidence is missing
- **WHEN** required evidence for a paid pilot claim is missing
- **THEN** the proposal kit SHALL require the claim to disclose the missing evidence and avoid presenting the lane as clean pass.

### Requirement: Pilot commercial proposal kit avoids private customer data
The proposal kit SHALL keep customer-specific terms, payment data, repository secrets, source code, private issue or pull request content, and signed legal text outside committed artifacts.

#### Scenario: Filled proposal is customer-specific
- **WHEN** an operator adapts the proposal kit for a real customer
- **THEN** the filled proposal SHALL be stored outside the public repository or in a private customer-controlled delivery folder.

#### Scenario: Proposal verifier finds sensitive material
- **WHEN** the proposal kit verifier detects obvious secret, payment, customer-private, or signed-contract marker material in committed proposal artifacts
- **THEN** it SHALL emit status `blocking` and identify the affected check without echoing the sensitive value.

### Requirement: Pilot commercial proposal kit has verification evidence
The system SHALL provide machine-readable JSON and operator-readable Markdown verification evidence for the proposal kit.

#### Scenario: Proposal kit verification passes
- **WHEN** required proposal kit documents exist and include required boundary, evidence, acceptance, support, renewal, and deferred-capability references
- **THEN** the verifier SHALL emit JSON and Markdown with status `pass`.

#### Scenario: Proposal kit verification finds gaps
- **WHEN** required proposal kit documents or references are missing
- **THEN** the verifier SHALL emit `warning` or `blocking` with missing document or missing reference details.
