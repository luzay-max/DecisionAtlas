# commercial-sales-enablement-kit Specification

## Purpose
Define buyer-facing sales enablement materials and verification requirements for DecisionAtlas self-hosted/private-deployment pilots.

## Requirements

### Requirement: Sales enablement kit provides buyer-facing materials
The system SHALL provide buyer-facing sales enablement materials for the self-hosted product route.

#### Scenario: A pilot evaluator reviews the product
- **WHEN** the evaluator opens the sales enablement kit
- **THEN** it MUST include a sales page draft, one-page product brief, and use-case briefs

#### Scenario: Commercial scope is described
- **WHEN** the materials describe the product route
- **THEN** they MUST position DecisionAtlas as self-hosted/private-deployment-first and disclose deferred SaaS capabilities

### Requirement: Sales enablement kit includes concrete use cases
The sales enablement kit SHALL include concrete use cases tied to current product capabilities.

#### Scenario: Use cases are reviewed
- **WHEN** the use-case material is opened
- **THEN** it MUST cover Code Decision Audit, Team Self-hosted Governance Workflow, and Release Evidence Handoff

### Requirement: Sales enablement kit is verifiable
The sales enablement kit SHALL be verified by local CI scripts.

#### Scenario: Verification runs
- **WHEN** the pilot kit verifier runs
- **THEN** it MUST check required sales enablement files and required commercial-boundary references
