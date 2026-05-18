## ADDED Requirements

### Requirement: Platform baseline supports self-hosted commercial packaging
The platform baseline SHALL distinguish near-term self-hosted commercial packaging from full hosted SaaS platform capabilities.

#### Scenario: Self-hosted packaging is described
- **WHEN** product or platform documentation describes the near-term commercial baseline
- **THEN** it SHALL describe Community, Team Self-hosted, and Enterprise Self-hosted as the current packaging direction
- **AND** it SHALL tie those tiers to local/private deployment, owner-scoped workspace behavior, evidence generation, and support boundaries.

#### Scenario: Hosted SaaS remains optional future scope
- **WHEN** platform documentation discusses billing, hosted multi-tenancy, full SaaS organization administration, Marketplace or self-service OAuth installation, or hosted secret custody
- **THEN** it SHALL identify those capabilities as future optional hosted managed service work rather than prerequisites for the self-hosted baseline.
