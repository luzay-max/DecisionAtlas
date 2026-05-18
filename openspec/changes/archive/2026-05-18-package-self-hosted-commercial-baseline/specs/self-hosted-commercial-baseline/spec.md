## ADDED Requirements

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
