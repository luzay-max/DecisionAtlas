# pilot-customer-delivery-kit Specification

## Purpose
Define customer-readable pilot delivery materials and verification evidence for DecisionAtlas self-hosted evaluations.

## Requirements

### Requirement: Pilot customer delivery kit is customer-readable
The system SHALL provide a pilot customer delivery kit that explains DecisionAtlas value, deployment path, evidence expectations, support boundary, and feedback loop without requiring source-code knowledge.

#### Scenario: Customer opens the delivery kit
- **WHEN** a prospective pilot customer or operator opens the delivery kit
- **THEN** the material SHALL include a one-page product explanation, target user, core use cases, deployment model, expected pilot outcome, and links to setup and evidence documents

#### Scenario: Deferred product lanes are disclosed
- **WHEN** the delivery kit describes current scope
- **THEN** it SHALL disclose that billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, online license server, and runtime license enforcement are not included in the current self-hosted pilot package

### Requirement: Pilot kit includes operational customer materials
The delivery kit SHALL include operational materials that a customer can use during evaluation.

#### Scenario: Demo script is available
- **WHEN** a maintainer or operator prepares a pilot demo
- **THEN** the kit SHALL provide a 10-minute demo script covering repository import, decision review, why-search, drift review, evidence generation, and known limitations

#### Scenario: Deployment checklist is available
- **WHEN** a pilot operator prepares deployment
- **THEN** the kit SHALL provide a deployment checklist covering prerequisites, environment variables, startup, admin initialization, repository import, readiness evidence, clean install rehearsal, and support handoff

#### Scenario: Customer FAQ is available
- **WHEN** a pilot customer reviews adoption risks
- **THEN** the kit SHALL include FAQ coverage for data custody, private repository access, team roles, evidence outputs, backup/restore, upgrade, support, pricing boundaries, and deferred capabilities

### Requirement: Pilot kit defines commercial and support packaging
The delivery kit SHALL explain Community, Team Self-hosted, and Enterprise Self-hosted differences without implying runtime license enforcement.

#### Scenario: Tier comparison is reviewed
- **WHEN** a customer compares editions
- **THEN** the kit SHALL distinguish product capability, deployment scope, support expectation, upgrade path, and enterprise customization boundary
- **AND** it SHALL state that runtime license enforcement remains deferred

#### Scenario: Pilot extension path is reviewed
- **WHEN** a pilot cannot be completed within the initial evaluation period
- **THEN** the kit SHALL explain how to request extension, what evidence must be preserved, and what follow-up decisions are required

### Requirement: Pilot kit verification evidence is generated
The system SHALL provide machine-readable and Markdown verification evidence for the pilot customer delivery kit.

#### Scenario: Delivery kit verification passes
- **WHEN** required pilot delivery materials exist and include required evidence references
- **THEN** the verifier SHALL emit status `pass`, checked items, output paths, and recommended next actions

#### Scenario: Required material is missing
- **WHEN** a required pilot delivery document, template, or required reference is missing
- **THEN** the verifier SHALL emit status `blocking` and identify the missing item

#### Scenario: Optional customer-specific evidence is absent
- **WHEN** customer-specific entitlement, signed agreement, or private repository evidence is absent
- **THEN** the verifier SHALL preserve that lane as `operator_guided` or `not_provided` rather than treating it as pass
