## ADDED Requirements

### Requirement: Browser rehearsal follows the core human workflow
The system SHALL provide a browser-driven rehearsal for the core DecisionAtlas human workflow.

#### Scenario: Operator walks the main product path
- **WHEN** the browser rehearsal starts from the homepage
- **THEN** it SHALL verify onboarding, workspace entry, review, why-search, drift, evidence center, and team permission surfaces are reachable in one human workflow.

#### Scenario: Workflow preserves workspace context
- **WHEN** the browser rehearsal moves from workspace dashboard to review, search, drift, evidence, or decision detail
- **THEN** the destination SHALL preserve or clearly display the active workspace context.

### Requirement: Browser rehearsal uses real repository context
The browser rehearsal SHALL include a real public GitHub repository reference in the tested flow.

#### Scenario: Real public repository reference is shown
- **WHEN** the browser rehearsal exercises repository or imported workspace behavior
- **THEN** it SHALL use and assert a real public GitHub repository URL or owner/name reference rather than only a placeholder repository.

#### Scenario: Live import is unavailable
- **WHEN** the rehearsal uses mocked responses, seeded data, or cannot complete live import because services or provider access are unavailable
- **THEN** it SHALL keep that limitation explicit and SHALL NOT claim successful live repository import.

### Requirement: Browser rehearsal validates role separation
The browser rehearsal SHALL verify that self-hosted team roles preserve the intended division of work.

#### Scenario: Reviewer or viewer opens team management
- **WHEN** a reviewer or viewer account opens team management
- **THEN** the UI SHALL show their role and deny admin-only account or permission management actions.

#### Scenario: Admin creates team accounts
- **WHEN** an admin creates reviewer or viewer accounts during the rehearsal
- **THEN** those accounts SHALL be usable for sign-in and role-specific UI checks.

### Requirement: Browser rehearsal produces durable evidence
The system SHALL record browser rehearsal expectations and validation results in project evidence or update logs.

#### Scenario: Rehearsal is completed
- **WHEN** the browser rehearsal passes locally or in CI
- **THEN** the update log or readiness material SHALL record the command, scope, result, and any non-clean limitations.

#### Scenario: Rehearsal is blocked
- **WHEN** the browser rehearsal cannot run because the stack, browser driver, provider, or Docker service is unavailable
- **THEN** the result SHALL be recorded as blocked, warning, or operator-guided rather than omitted.
