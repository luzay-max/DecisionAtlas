## ADDED Requirements

### Requirement: Self-hosted license tiers are documented
The system SHALL provide customer-readable documentation that defines Community, Team Self-hosted, and Enterprise Self-hosted product boundaries.

#### Scenario: Customer reviews tier boundary
- **WHEN** an operator or customer opens the license/support boundary documentation
- **THEN** it SHALL explain intended audience, allowed evaluation scope, paid support scope, upgrade access, and explicitly excluded capabilities for each tier

#### Scenario: Deferred capabilities remain explicit
- **WHEN** the documentation describes paid packaging
- **THEN** it SHALL preserve deferred capabilities including SaaS billing, hosted multi-tenancy, marketplace or self-service OAuth, enterprise SSO, hosted secret vault, and runtime license enforcement

### Requirement: Offline entitlement template is available
The system SHALL provide a local entitlement template that can record offline deployment and support boundary metadata.

#### Scenario: Entitlement template is reviewed
- **WHEN** an operator opens the entitlement template
- **THEN** it SHALL include schema version, customer label, tier, deployment scope, support start/end dates, seat/workspace/repository guidance, upgrade channel, support contact, and notes

#### Scenario: Entitlement avoids secrets
- **WHEN** the entitlement template is included in package or handoff evidence
- **THEN** it SHALL NOT require tokens, repository credentials, private source contents, billing secrets, or personal payment information

### Requirement: License boundary is non-blocking for evaluation
The system SHALL avoid strong runtime license enforcement in this stage.

#### Scenario: Entitlement is missing during local evaluation
- **WHEN** a local evaluator runs the self-hosted package without entitlement evidence
- **THEN** the core package and report tooling SHALL remain usable and SHALL record the entitlement lane as not provided or operator-guided rather than blocking runtime

#### Scenario: Customer handoff discloses missing boundary
- **WHEN** a customer handoff report is generated without license/support boundary evidence
- **THEN** the report SHALL disclose the missing boundary as a non-clean state before a clean paid-customer claim is made
