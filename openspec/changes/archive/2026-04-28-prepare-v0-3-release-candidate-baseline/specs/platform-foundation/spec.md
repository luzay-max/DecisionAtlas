## ADDED Requirements

### Requirement: v0.3 platform baseline distinguishes productized flows from full SaaS
The system SHALL describe the v0.3 platform baseline as productized owner-scoped access and workspace lifecycle flows while keeping full SaaS administration outside the release-candidate scope.

#### Scenario: Productized flows are included in the baseline
- **WHEN** the v0.3 release candidate describes platform capabilities
- **THEN** it SHALL include authenticated session recovery, owner-scope switching, role-gated product actions, GitHub App installation binding, and token-backed private repository access binding

#### Scenario: Full SaaS capabilities remain out of scope
- **WHEN** the v0.3 release candidate describes platform limitations
- **THEN** it SHALL state that billing, org administration, secret vault, GitHub Marketplace/OAuth self-service installation, and collaborative review workflows are not included

#### Scenario: Follow-up work starts from the RC baseline
- **WHEN** later platform hardening changes are proposed
- **THEN** they SHALL identify whether they harden the v0.3 RC baseline or introduce capabilities beyond that baseline
