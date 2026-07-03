# mimo-ui-smoke-coverage Specification

## Purpose
Define browser and component-test coverage expectations for the Mimo branch UI shell, onboarding, sidebar navigation, evidence/settings surfaces, and demo workspace flow.

## Requirements

### Requirement: Page-content unit tests isolate global sidebar dependencies
The test suite SHALL keep review, drift, and timeline page-content unit tests focused on page content behavior without requiring the full global sidebar theme/navigation provider tree.

#### Scenario: Page-content tests render without theme provider failures
- **WHEN** review, drift, or timeline page-content unit tests render the component directly
- **THEN** the tests SHALL not fail because `GlobalSidebar`, `ThemeToggle`, or `useTheme` requires an app-level provider.

#### Scenario: Page behavior remains asserted
- **WHEN** sidebar dependencies are isolated in page-content unit tests
- **THEN** the tests SHALL still assert page-specific review, drift, timeline, provenance, and action behavior.

### Requirement: Mimo UI browser smoke covers customer-visible shell paths
The test suite SHALL provide a Playwright browser smoke for the `mimo` UI shell and onboarding path.

#### Scenario: Homepage onboarding is visible
- **WHEN** the Mimo UI smoke opens the homepage
- **THEN** it SHALL verify the DecisionAtlas identity, onboarding guide, quick action links, and next-step links.

#### Scenario: Operator pages are visible
- **WHEN** the Mimo UI smoke opens settings and evidence pages
- **THEN** it SHALL verify configuration, system status, evidence dashboard, and report command surfaces are visible.

#### Scenario: Recovery path is visible
- **WHEN** the Mimo UI smoke opens an unknown route
- **THEN** it SHALL verify the 404 recovery suggestions and home link are visible.

#### Scenario: Demo workspace navigation works
- **WHEN** the Mimo UI smoke opens the demo workspace path
- **THEN** it SHALL verify review, why-search, and drift navigation remain reachable in a real browser.

### Requirement: Local browser smoke prerequisites are explicit
The local verification flow SHALL document and preserve the setup assumptions needed for Mimo UI smoke execution.

#### Scenario: Local proxy variables interfere with localhost checks
- **WHEN** local proxy variables route localhost webServer checks through an invalid proxy
- **THEN** the smoke command SHALL be run with localhost proxy variables cleared or bypassed.

#### Scenario: Workspace dependencies are not linked
- **WHEN** `apps/web` or `apps/api` dependencies are missing from workspace links
- **THEN** the operator SHALL restore package links before treating Playwright smoke failures as product failures.

### Requirement: Mimo browser coverage includes human workflow rehearsal
Mimo browser coverage SHALL include a human workflow rehearsal in addition to page-level smoke checks.

#### Scenario: Human workflow rehearsal runs
- **WHEN** Mimo browser tests are executed for release or product-flow validation
- **THEN** at least one test SHALL exercise homepage onboarding, workspace context, review, why-search, drift, evidence center, and team role checks in a real browser.

#### Scenario: Browser test identifies mocked provider lanes
- **WHEN** Mimo browser tests stub API responses or use seeded data for deterministic execution
- **THEN** the test or related documentation SHALL distinguish browser workflow proof from live provider/import proof.
