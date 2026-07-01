## ADDED Requirements

### Requirement: CI uses Node 24-compatible GitHub Actions
The CI workflow SHALL use GitHub Action major versions that are compatible with the current GitHub-hosted runner JavaScript action runtime.

#### Scenario: CI validates without action runtime deprecation
- **WHEN** the CI workflow runs on a pull request or push
- **THEN** the workflow MUST avoid Node.js 20 action deprecation warnings caused by outdated action major versions

#### Scenario: Existing validation scope is preserved
- **WHEN** action versions are upgraded
- **THEN** CI MUST still run Node tests, typecheck, engine tests, benchmark fixture validation, and browser smoke validation

### Requirement: CI runner image is explicit
The CI workflow SHALL pin the Windows runner image explicitly for release validation instead of relying on `windows-latest` alias migration behavior.

#### Scenario: Runner alias migration does not change CI implicitly
- **WHEN** GitHub changes the target of the `windows-latest` alias
- **THEN** the CI workflow MUST continue using the configured explicit Windows runner image
