## ADDED Requirements

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
