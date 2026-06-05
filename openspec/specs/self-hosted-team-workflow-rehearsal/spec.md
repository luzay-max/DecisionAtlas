## Purpose

Define repeatable operator and browser evidence for proving the small-team self-hosted account, permission, and workspace workflow.

## Requirements

### Requirement: Browser rehearsal covers the team workflow
The project SHALL provide a repeatable browser rehearsal that exercises the small-team self-hosted workflow from a human operator perspective.

#### Scenario: Admin verifies team management surface
- **WHEN** an operator runs the self-hosted team browser rehearsal
- **THEN** the rehearsal SHALL visit the team management surface as an admin
- **THEN** it SHALL verify account-management and workspace-membership controls are visible

#### Scenario: Non-admin sees permission boundary
- **WHEN** the rehearsal evaluates a reviewer or viewer role
- **THEN** the product SHALL explain that admin role is required for team management
- **THEN** account-management controls SHALL remain unavailable

### Requirement: Rehearsal preserves backend authority
The team workflow rehearsal SHALL not rely only on hidden frontend controls for permission proof.

#### Scenario: Role boundary remains backed by API tests
- **WHEN** the browser rehearsal claims reviewer or viewer boundaries
- **THEN** the validation evidence SHALL include backend/API coverage for rejected unauthorized mutations
- **THEN** browser evidence SHALL be treated as product usability proof rather than the only security proof

### Requirement: Optional live public repository evidence is explicit
The self-hosted team rehearsal SHALL support optional live public GitHub repository evidence without making deterministic CI depend on external network state.

#### Scenario: Operator records live public repository check
- **WHEN** an operator runs a live public GitHub repository import or benchmark as part of the rehearsal
- **THEN** the selected repository, status, generated report path, and any external blocker SHALL be recorded
- **THEN** missing or blocked live evidence SHALL be disclosed rather than converted into a clean pass

### Requirement: Operator documentation links rehearsal to delivery readiness
The project SHALL document how to run and interpret the self-hosted team workflow rehearsal.

#### Scenario: Operator prepares self-hosted handoff
- **WHEN** an operator prepares a Team Self-hosted delivery or pilot handoff
- **THEN** documentation SHALL identify the browser rehearsal, backend role-boundary tests, and optional live public repository evidence required for the handoff
- **THEN** documentation SHALL preserve the current non-goals of SaaS billing, marketplace OAuth, Git hosting, SSO, and license enforcement
