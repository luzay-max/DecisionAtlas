## Purpose
Define Markdown governance document ingest, rule-draft extraction, and human review behavior.
## Requirements
### Requirement: Markdown governance documents can be imported with bounded metadata
The system SHALL allow an authenticated owner-scoped actor to import Markdown governance documents with bounded document type, title, scope, source path, status, and content hash metadata.

#### Scenario: Import valid markdown governance document
- **WHEN** an admin imports Markdown content with a supported governance document type
- **THEN** the system SHALL persist the document in the current owner scope and return its metadata

#### Scenario: Reject unsupported document type
- **WHEN** an import request uses an unsupported governance document type
- **THEN** the system SHALL reject the request with a bounded validation error

#### Scenario: Preserve source traceability
- **WHEN** a document is imported with source path or source label metadata
- **THEN** the system SHALL preserve that source metadata without requiring the document to come from a repository import

### Requirement: Governance rule drafts are extracted for human review
The system SHALL create reviewable governance rule drafts from imported Markdown using deterministic extraction that does not require live AI provider credentials, SHALL reduce extraction of ordinary descriptive prose, and SHALL preserve bounded extraction metadata that helps reviewers understand why each draft was created.

#### Scenario: Extract heading-based rule draft
- **WHEN** an imported Markdown document contains a rule-like heading and descriptive body with explicit rule signal such as a `Rule:` heading, supported severity marker, normative checklist command, postmortem lesson marker, decision outcome marker, or anti-pattern prohibition
- **THEN** the system SHALL create a rule draft with title, description, source document, source excerpt, severity, scope, rule type, extraction reason, and pending review status

#### Scenario: Avoid extracting ordinary prose
- **WHEN** an imported Markdown section contains ordinary descriptive prose that merely uses generic modal language without an explicit governance rule signal
- **THEN** the system SHALL persist the document but SHALL NOT create a rule draft for that section

#### Scenario: Extract severity and scope markers
- **WHEN** a Markdown section includes bounded `Severity:` or `Scope:` markers
- **THEN** the extracted draft SHALL preserve those values when supported and SHALL fall back to safe defaults otherwise

#### Scenario: Infer document-type-aware rule classification
- **WHEN** a Markdown governance document is imported as a standard, postmortem, decision record, or anti-pattern document
- **THEN** extracted drafts SHALL include bounded rule classification metadata that reflects the source document type and extraction signal

#### Scenario: Empty markdown creates no accepted rules
- **WHEN** imported Markdown does not contain extractable governance rules
- **THEN** the system SHALL persist the document but SHALL NOT create accepted governance rules automatically

### Requirement: Governance rule drafts require human review before becoming accepted rules
The system SHALL let humans accept or reject rule drafts with optional bounded review rationale, and SHALL only expose accepted active governance rules as durable rules for future checker work.

#### Scenario: Accept governance rule draft
- **WHEN** a reviewer accepts a pending governance rule draft and provides review rationale
- **THEN** the system SHALL mark the draft accepted, preserve the reviewer, review time, and review rationale, and expose it in the accepted governance rules list with source traceability

#### Scenario: Reject governance rule draft
- **WHEN** a reviewer rejects a pending governance rule draft and provides review rationale
- **THEN** the system SHALL mark the draft rejected, preserve the reviewer, review time, and review rationale, and SHALL NOT expose it as an accepted governance rule

#### Scenario: Accepted rules remain source-linked
- **WHEN** an accepted governance rule is listed
- **THEN** the response SHALL include its source document id, source title, source excerpt, severity, scope, rule type, extraction reason, review rationale, lifecycle metadata, and review metadata

#### Scenario: Non-authoritative lifecycle states are not accepted rules
- **WHEN** a rule draft is pending, rejected, stale, or superseded
- **THEN** the system SHALL NOT expose that draft as an active accepted governance rule for checker use

### Requirement: Governance ingest has a minimal product surface
The product SHALL provide a minimal surface for importing Markdown governance documents, listing imported documents, reviewing pending rule drafts with rationale, filtering accepted rule drafts, and inspecting source evidence.

#### Scenario: User imports markdown from product surface
- **WHEN** an admin submits Markdown governance content through the product surface
- **THEN** the product SHALL show the imported document and extracted pending drafts

#### Scenario: User reviews rule draft from product surface
- **WHEN** a reviewer accepts or rejects a governance rule draft from the product surface
- **THEN** the product SHALL submit the selected review state and review rationale, update the draft status without requiring a page reload, and display the stored review rationale

#### Scenario: User filters accepted rules
- **WHEN** accepted governance rules exist with different scopes, severities, rule types, or lifecycle states
- **THEN** the product SHALL let the reviewer filter or narrow the accepted rule list by those bounded fields

#### Scenario: User inspects extraction evidence
- **WHEN** a pending or accepted rule draft is rendered
- **THEN** the product SHALL show source title, source excerpt preview, extraction reason, rule type, severity, scope, and review rationale when available

#### Scenario: Product explains no automatic enforcement
- **WHEN** the governance page renders
- **THEN** it SHALL state that accepted rules are stored for later checker work and are not yet CI blockers

### Requirement: Governance rule lifecycle metadata is prepared
The system SHALL preserve bounded lifecycle metadata for governance rule drafts so stale or superseded rules can be represented without automatic replacement.

#### Scenario: Active accepted rule remains current by default
- **WHEN** a reviewer accepts a rule draft without specifying lifecycle metadata
- **THEN** the system SHALL keep the rule active and current by default

#### Scenario: Superseded rule is represented without automatic replacement
- **WHEN** a rule draft is marked superseded by a human or future workflow
- **THEN** the system SHALL preserve the superseded state and optional supersession reference without automatically accepting, rejecting, or rewriting other rules

#### Scenario: Stale rule is non-authoritative for checker input
- **WHEN** a rule draft is marked stale
- **THEN** the system SHALL preserve the stale state and SHALL NOT expose that rule as active accepted checker input

### Requirement: Governance Markdown ingest is demoable as a human-reviewed lane
The system SHALL describe governance Markdown ingest during hosted preview as a bounded human-reviewed workflow that imports documents, creates rule drafts, and requires explicit human acceptance before rules become authoritative checker input.

#### Scenario: Preview walkthrough imports governance Markdown safely
- **WHEN** an operator demonstrates governance Markdown ingest during hosted preview
- **THEN** the walkthrough SHALL show or describe imported documents and pending rule drafts without implying that drafts are accepted automatically

#### Scenario: Accepted rules are shown with source evidence
- **WHEN** a governed hosted preview includes accepted governance rules
- **THEN** the operator guidance SHALL require source title, source excerpt, extraction reason, review rationale, or equivalent traceability to be visible or explainable

#### Scenario: Ingest demo avoids secret and production-policy claims
- **WHEN** governance Markdown content is used in a hosted preview
- **THEN** the guidance SHALL require non-sensitive demo content or operator-approved content and SHALL avoid presenting the flow as a full enterprise policy-management system

### Requirement: Governance ingest readiness has bounded validation evidence
The system SHALL identify deterministic validation evidence for the governance Markdown ingest lane before it is shown in a governed hosted preview.

#### Scenario: Ingest readiness cites targeted validation
- **WHEN** an operator records governed hosted preview readiness
- **THEN** the report SHALL identify whether governance Markdown ingest and rule review behavior was validated by targeted tests, local product smoke, hosted product smoke, or marked operator-guided

#### Scenario: Missing governance content is non-blocking by default
- **WHEN** the stable guided demo works but governance demo content is unavailable
- **THEN** readiness guidance SHALL classify the governance lane as non-blocking or known limitation unless the preview explicitly depends on demonstrating governance ingest
