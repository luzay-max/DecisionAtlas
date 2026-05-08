## ADDED Requirements

### Requirement: Release-facing docs distinguish development protocol from release gates
The system SHALL keep the default local governance development protocol distinct from canonical release validation and optional enforcement preview.

#### Scenario: Docs identify canonical release gate
- **WHEN** release-facing docs mention the default governance development protocol
- **THEN** they SHALL continue to identify the canonical local release gate as the mandatory deterministic release validation path

#### Scenario: Docs identify development protocol scope
- **WHEN** developers or AI agents read workflow guidance
- **THEN** the docs SHALL describe the default governance development protocol as local workflow guidance for preflight, postflight, archive, commit, and handoff behavior

#### Scenario: Docs identify enforcement preview as opt-in
- **WHEN** docs mention enforcement preview or strict exit behavior
- **THEN** they SHALL state that enforcement preview remains opt-in and is not default CI enforcement

### Requirement: Release checklist records governance protocol evidence
The system SHALL allow release and readiness records to include governance protocol evidence without making advisory guardrail status a default release blocker.

#### Scenario: Checklist can record protocol status
- **WHEN** a maintainer prepares release or readiness evidence
- **THEN** the checklist MAY record the latest protocol status, guardrail status, recommended actions, and human questions as advisory evidence

#### Scenario: Advisory status does not replace release gate
- **WHEN** protocol status is recorded in release or readiness evidence
- **THEN** the documentation SHALL state that it does not replace the canonical release baseline command

#### Scenario: Pause evidence requires human decision before positive claims
- **WHEN** protocol status reports `pause` during release or hosted-preview preparation
- **THEN** release-facing guidance SHALL require a human decision before using that status as positive readiness evidence
