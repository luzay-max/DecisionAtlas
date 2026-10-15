## Purpose

Define the post-full-chain product roadmap after top-level full-chain rehearsal evidence exists.

## Requirements

### Requirement: Post-full-chain roadmap is documented
The project SHALL maintain a post-full-chain roadmap after full-chain random repository release rehearsal exists.

#### Scenario: Roadmap is written
- **WHEN** full-chain evidence exists
- **THEN** the roadmap SHALL describe current proof, remaining warning boundaries, next OpenSpec candidates, and stop/continue rules.

#### Scenario: Customer-host proof remains incomplete
- **WHEN** customer-host v2 evidence is template-only or local-only
- **THEN** the roadmap SHALL keep real external/customer host proof as the highest-priority validation item.

### Requirement: Roadmap remains evidence-gated
The post-full-chain roadmap SHALL order future work by evidence value.

#### Scenario: Feature expansion is considered
- **WHEN** billing, marketplace, hosted multi-tenancy, organization management, or broader enterprise features are considered
- **THEN** the roadmap SHALL defer them unless real self-hosted customer trial evidence creates a concrete need.
