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
The system SHALL create reviewable governance rule drafts from imported Markdown using deterministic extraction that does not require live AI provider credentials.

#### Scenario: Extract heading-based rule draft
- **WHEN** an imported Markdown document contains a rule-like heading and descriptive body
- **THEN** the system SHALL create a rule draft with title, description, source document, source excerpt, severity, scope, and pending review status

#### Scenario: Extract severity and scope markers
- **WHEN** a Markdown section includes bounded `Severity:` or `Scope:` markers
- **THEN** the extracted draft SHALL preserve those values when supported and SHALL fall back to safe defaults otherwise

#### Scenario: Empty markdown creates no accepted rules
- **WHEN** imported Markdown does not contain extractable governance rules
- **THEN** the system SHALL persist the document but SHALL NOT create accepted governance rules automatically

### Requirement: Governance rule drafts require human review before becoming accepted rules
The system SHALL let humans accept or reject rule drafts, and SHALL only expose accepted governance rules as durable rules for future checker work.

#### Scenario: Accept governance rule draft
- **WHEN** a reviewer accepts a pending governance rule draft
- **THEN** the system SHALL mark the draft accepted and expose it in the accepted governance rules list with source traceability

#### Scenario: Reject governance rule draft
- **WHEN** a reviewer rejects a pending governance rule draft
- **THEN** the system SHALL mark the draft rejected and SHALL NOT expose it as an accepted governance rule

#### Scenario: Accepted rules remain source-linked
- **WHEN** an accepted governance rule is listed
- **THEN** the response SHALL include its source document id, source title, source excerpt, severity, and scope

### Requirement: Governance ingest has a minimal product surface
The product SHALL provide a minimal surface for importing Markdown governance documents, listing imported documents, and reviewing pending or accepted rule drafts.

#### Scenario: User imports markdown from product surface
- **WHEN** an admin submits Markdown governance content through the product surface
- **THEN** the product SHALL show the imported document and extracted pending drafts

#### Scenario: User reviews rule draft from product surface
- **WHEN** a reviewer accepts or rejects a governance rule draft
- **THEN** the product SHALL update the draft status without requiring a page reload

#### Scenario: Product explains no automatic enforcement
- **WHEN** the governance page renders
- **THEN** it SHALL state that accepted rules are stored for later checker work and are not yet CI blockers
