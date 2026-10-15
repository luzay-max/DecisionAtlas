## ADDED Requirements

### Requirement: Audit report references real continuity readiness
Code Decision Audit reports SHALL reference real backup/restore/upgrade rehearsal evidence when sanitized evidence is provided.

#### Scenario: Real continuity evidence is supplied
- **WHEN** the Code Decision Audit report builder receives real continuity rehearsal evidence
- **THEN** the audit report MUST summarize continuity status, scratch scope, restore validation status, post-upgrade status, rollback plan status, limitations, and customer-readiness implications

#### Scenario: Real continuity evidence is omitted
- **WHEN** real continuity rehearsal evidence is not supplied
- **THEN** the audit report MUST preserve tested continuity evidence as `not_provided` or `operator_guided` and MUST NOT claim tested backup/restore/upgrade readiness

#### Scenario: Real continuity evidence is unsafe
- **WHEN** supplied real continuity evidence contains sensitive material or blocked redaction status
- **THEN** the audit report builder MUST reject the evidence or include only a bounded blocked summary without exposing sensitive content
