## ADDED Requirements

### Requirement: Mimo browser coverage includes human workflow rehearsal
Mimo browser coverage SHALL include a human workflow rehearsal in addition to page-level smoke checks.

#### Scenario: Human workflow rehearsal runs
- **WHEN** Mimo browser tests are executed for release or product-flow validation
- **THEN** at least one test SHALL exercise homepage onboarding, workspace context, review, why-search, drift, evidence center, and team role checks in a real browser.

#### Scenario: Browser test identifies mocked provider lanes
- **WHEN** Mimo browser tests stub API responses or use seeded data for deterministic execution
- **THEN** the test or related documentation SHALL distinguish browser workflow proof from live provider/import proof.
