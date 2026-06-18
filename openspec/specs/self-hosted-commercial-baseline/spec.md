# self-hosted-commercial-baseline Specification

## Purpose
TBD - created by archiving change package-self-hosted-commercial-baseline. Update Purpose after archive.
## Requirements
### Requirement: Self-hosted product tiers are documented
The system SHALL document a self-hosted product packaging baseline with clear Community, Team Self-hosted, and Enterprise Self-hosted boundaries.

#### Scenario: Product tiers are described
- **WHEN** a prospective customer or operator reads the self-hosted product documentation
- **THEN** the documentation SHALL describe Community, Team Self-hosted, and Enterprise Self-hosted capabilities
- **AND** it SHALL distinguish product capabilities from support, deployment, and commercial packaging.

#### Scenario: SaaS capabilities are deferred
- **WHEN** the documentation describes current product limitations
- **THEN** it SHALL state that billing, full SaaS organization management, hosted multi-tenancy, Marketplace or self-service OAuth installation, and secret vault behavior are not part of the self-hosted baseline.

### Requirement: Self-hosted deployment path is customer-readable
The system SHALL provide a customer-readable self-hosted setup path that explains how to bring up and verify DecisionAtlas outside the maintainer's machine.

#### Scenario: Operator follows self-hosted setup
- **WHEN** an operator prepares a self-hosted evaluation or private deployment
- **THEN** the documentation SHALL identify required services, required environment variables, provider configuration, startup commands, verification commands, and expected service URLs.

#### Scenario: Operator validates readiness
- **WHEN** an operator completes self-hosted startup
- **THEN** the documentation SHALL point to health, smoke, release evidence, hosted readiness, governance guardrail, benchmark comparison, and readiness evidence history commands as applicable validation evidence.

### Requirement: Private repository and credential boundaries are explicit
The system SHALL document how private repository access and provider credentials are handled in self-hosted deployments.

#### Scenario: Private repository access is configured
- **WHEN** an operator enables private repository access in a self-hosted deployment
- **THEN** the documentation SHALL explain supported access paths, minimum permission expectations, validation steps, and troubleshooting categories.

#### Scenario: Credential custody is described
- **WHEN** documentation mentions provider keys or repository credentials
- **THEN** it SHALL state that credentials remain in the customer's self-hosted environment or backend surfaces
- **AND** it SHALL disclose that no hosted secret vault is included in the baseline.

### Requirement: Self-hosted support and upgrade boundaries are documented
The system SHALL document support, limitation, backup, restore, and upgrade expectations for self-hosted users.

#### Scenario: Support boundary is reviewed
- **WHEN** a customer evaluates a self-hosted tier
- **THEN** the documentation SHALL identify what is community-guided, what is supported under paid self-hosted tiers, and what remains custom enterprise work.

#### Scenario: Upgrade and recovery expectations are reviewed
- **WHEN** an operator plans to upgrade or recover a self-hosted deployment
- **THEN** the documentation SHALL describe backup, restore, migration, reset, reseed, and rollback expectations using existing supported commands where possible.

### Requirement: Code Decision Audit handoff is available
The system SHALL provide a customer-readable Code Decision Audit or governance report template that turns existing DecisionAtlas evidence into a commercial handoff.

#### Scenario: Audit report is prepared
- **WHEN** DecisionAtlas is used to evaluate a real repository for a customer
- **THEN** the report template SHALL include decision map summary, accepted decision evidence, why-search examples, drift findings, governance guardrail status, release evidence, benchmark comparison, readiness evidence history, limitations, and recommended next actions.

#### Scenario: Audit report preserves evidence boundaries
- **WHEN** evidence includes warning, operator-guided, not-provided, known-limitation, or blocking states
- **THEN** the report template SHALL disclose those states rather than presenting the audit as a clean pass.

### Requirement: Self-hosted baseline avoids premature license enforcement
The system SHALL define commercial packaging and support boundaries without requiring runtime license enforcement in the first self-hosted baseline.

#### Scenario: Edition boundaries are documented
- **WHEN** Community, Team Self-hosted, and Enterprise Self-hosted are described
- **THEN** the documentation SHALL frame them as product/support packaging boundaries
- **AND** it SHALL NOT require runtime license validation as part of this baseline.

### Requirement: Self-hosted customer handoff references rehearsal evidence
The system SHALL require self-hosted customer handoff claims to reference completed rehearsal evidence or disclose why rehearsal evidence is missing.

#### Scenario: Handoff claims readiness
- **WHEN** documentation, release notes, or customer handoff material claims that a self-hosted deployment is ready for evaluation or pilot use
- **THEN** the material SHALL reference a completed self-hosted delivery rehearsal, readiness evidence history entry, or equivalent evidence package
- **AND** it SHALL disclose any warning, blocking, operator-guided, known-limitation, or not-provided states.

#### Scenario: Rehearsal evidence is missing
- **WHEN** a handoff is prepared without completed rehearsal evidence
- **THEN** the handoff SHALL state that rehearsal evidence is missing
- **AND** it SHALL avoid claiming clean self-hosted readiness.

### Requirement: Self-hosted commercial claims reference package artifacts
The self-hosted commercial baseline SHALL require customer-facing package claims to reference generated package artifacts and operator runbooks.

#### Scenario: Customer handoff references package manifest
- **WHEN** documentation, release notes, or customer handoff material claims that DecisionAtlas is packaged for self-hosted evaluation
- **THEN** the material SHALL reference a package manifest, package verification evidence, setup guide, environment template, and backup/restore/upgrade runbook coverage

#### Scenario: Package claim preserves support boundary
- **WHEN** a self-hosted package is described commercially
- **THEN** the documentation SHALL distinguish package contents from paid support, custom enterprise work, runtime license enforcement, managed hosted operations, and SaaS capabilities

#### Scenario: Missing package artifacts limit claim strength
- **WHEN** package manifest or package verification evidence is missing
- **THEN** the commercial baseline SHALL require the handoff to disclose the missing artifact and avoid claiming clean package readiness

### Requirement: Self-hosted commercial baseline references pilot delivery kit
The self-hosted commercial baseline SHALL require customer-facing pilot claims to reference pilot delivery kit materials.

#### Scenario: Pilot claim is made
- **WHEN** documentation or handoff material claims DecisionAtlas is ready for a self-hosted pilot
- **THEN** the material SHALL reference the pilot customer delivery kit, package guide, clean install rehearsal, handoff report, and license/support boundary

#### Scenario: Commercial boundary is discussed
- **WHEN** pricing, tiering, support, or pilot extension is discussed
- **THEN** the material SHALL distinguish Community, Team Self-hosted, and Enterprise Self-hosted boundaries
- **AND** it SHALL avoid presenting deferred SaaS, billing, Marketplace, enterprise SSO, or runtime license enforcement as implemented

### Requirement: Self-hosted commercial baseline distinguishes private-repo proof from template readiness
The self-hosted commercial baseline SHALL distinguish having a private-repo pilot evidence workflow from having completed a real private-repo pilot in a customer-controlled environment.

#### Scenario: Commercial baseline describes private-repo evidence
- **WHEN** self-hosted commercial documentation references private-repo pilot evidence
- **THEN** it SHALL state that the committed template and verifier prove evidence readiness only
- **AND** it SHALL require actual private-repo proof to be generated locally or in the customer-controlled environment without committing private content or credentials.

#### Scenario: Private-repo evidence is absent
- **WHEN** a customer-facing self-hosted claim lacks sanitized private-repo pilot evidence
- **THEN** the baseline SHALL require the claim to disclose the missing evidence and avoid describing private-repo readiness as clean pass.

### Requirement: Self-hosted commercial baseline distinguishes continuity readiness
The self-hosted commercial baseline SHALL distinguish deployable package readiness from backup, restore, upgrade, and rollback continuity readiness.

#### Scenario: Commercial claim references long-term operation
- **WHEN** documentation, sales material, release notes, or customer handoff claims long-term self-hosted operation readiness
- **THEN** it SHALL reference backup/restore/upgrade rehearsal evidence or disclose that continuity evidence remains missing, operator-guided, or known-limited.

#### Scenario: Continuity evidence is incomplete
- **WHEN** backup, restore, upgrade, or rollback rehearsal evidence is incomplete
- **THEN** the commercial baseline SHALL prevent clean continuity claims and require the limitation to remain visible.

### Requirement: Self-hosted commercial baseline references proposal kit
The self-hosted commercial baseline SHALL require paid pilot, quote, support, and renewal claims to reference bounded proposal kit materials rather than implying implemented billing or runtime license enforcement.

#### Scenario: Paid pilot offer is described
- **WHEN** self-hosted commercial documentation describes a paid pilot offer
- **THEN** it SHALL reference the pilot commercial proposal kit, support boundary, acceptance checklist, evidence requirements, and renewal or upgrade path.

#### Scenario: Billing or license enforcement is discussed
- **WHEN** pricing, quote, entitlement, renewal, or upgrade material is discussed
- **THEN** the baseline SHALL state that current materials are proposal templates and do not implement billing, online license activation, or runtime license enforcement.
