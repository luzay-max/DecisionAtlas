## ADDED Requirements

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
