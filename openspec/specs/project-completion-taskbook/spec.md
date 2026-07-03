# project-completion-taskbook Specification

## Purpose
Defines a living completion taskbook that maps DecisionAtlas product goals to current evidence, remaining gaps, and next OpenSpec changes.

## Requirements
### Requirement: Completion taskbook maps goals to evidence
The project SHALL maintain a completion taskbook that maps active product goals to current evidence and remaining work.

#### Scenario: Operator reviews completion state
- **WHEN** an operator opens the completion taskbook
- **THEN** it SHALL show each major goal area, status, evidence references, gaps, and next OpenSpec candidate.

#### Scenario: Evidence is weak or partial
- **WHEN** a product-readiness claim is supported only by partial, mocked, local-only, or operator-guided evidence
- **THEN** the taskbook SHALL mark the claim as partial rather than complete.

### Requirement: Completion taskbook preserves OpenSpec workflow
The completion taskbook SHALL guide future work through OpenSpec changes rather than ad hoc edits.

#### Scenario: Next work is selected
- **WHEN** the taskbook lists next development items
- **THEN** each implementation item SHALL have a suggested OpenSpec change name and acceptance evidence.

#### Scenario: Work is completed
- **WHEN** an OpenSpec change is archived
- **THEN** the taskbook SHALL be updated or referenced by the update log before claiming the related plan goal is complete.

### Requirement: Completion taskbook distinguishes not-now scope
The completion taskbook SHALL explicitly separate current self-hosted product completion from deferred hosted SaaS work.

#### Scenario: Deferred SaaS capability appears in planning
- **WHEN** billing, Marketplace, self-service OAuth, managed multi-tenancy, or hosted service operations appear in the roadmap
- **THEN** the taskbook SHALL classify them as not-now unless a new customer-driven OpenSpec change is proposed.
