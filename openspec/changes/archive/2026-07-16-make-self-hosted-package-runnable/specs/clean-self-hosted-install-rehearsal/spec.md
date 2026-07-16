## MODIFIED Requirements

### Requirement: Rehearsal verifies operator handoff entry points
The system SHALL verify the copied package exposes the minimum operator handoff and runnable application entry points.

#### Scenario: Required package assets are present
- **WHEN** the copied package is inspected
- **THEN** the system SHALL check for package manifest, README, environment template, self-hosted package guide, operations runbook, readiness checklist, delivery rehearsal doc, license/support boundary doc, startup launcher, package verifier, dependency manifests and lockfiles, Docker Compose support, application runtime, engine runtime and migrations, prompts, and package browser smoke entry points

#### Scenario: Required asset is missing
- **WHEN** a required operator handoff or runnable runtime asset is absent from the copied package
- **THEN** the system SHALL mark that check `blocking` and include the missing relative path

### Requirement: Clean install rehearsal distinguishes local clean checks from external host evidence
The clean self-hosted install rehearsal SHALL disclose that local clean workspace and independent hosted-runner checks are not substitutes for customer-controlled host install evidence.

#### Scenario: Local clean rehearsal is generated without external evidence
- **WHEN** clean install rehearsal evidence is generated without external install evidence
- **THEN** the report SHALL preserve local clean install status but SHALL mark external/customer-host install evidence as `not_provided` or `operator_guided`

#### Scenario: Independent GitHub runner rehearsal passes
- **WHEN** the package installs and completes runtime smoke on a fresh GitHub-hosted runner
- **THEN** the report SHALL record independent-host package evidence and SHALL keep `is_customer_controlled=false` and customer proof non-clean

#### Scenario: External evidence is referenced
- **WHEN** clean install rehearsal evidence receives an external install evidence JSON or Markdown path
- **THEN** the report SHALL reference the external evidence status and limitations without copying raw external evidence content

## ADDED Requirements

### Requirement: Runnable package is exercised from the isolated copy
The system SHALL support a bounded runtime rehearsal whose commands execute from the copied package root rather than the maintainer source checkout.

#### Scenario: Runtime preflight succeeds
- **WHEN** the copied package has compatible Node, pnpm, Python, uv, and required runtime assets
- **THEN** the rehearsal SHALL install or verify exact dependencies from lockfiles and report runtime preflight `pass`

#### Scenario: Service smoke succeeds
- **WHEN** the isolated package starts engine, API, and web services and all configured health probes succeed
- **THEN** the rehearsal SHALL report service startup `pass` with bounded URLs and durations

#### Scenario: Browser smoke succeeds
- **WHEN** a browser completes the bounded imported-workspace workflow against services started from the copied package
- **THEN** the rehearsal SHALL report browser smoke `pass` without recording credentials, raw repository contents, or raw model output

#### Scenario: Runtime command fails
- **WHEN** dependency installation, service startup, a health probe, or browser smoke fails
- **THEN** the rehearsal SHALL report `blocking` or `local_stack_failure` with the failed stage and bounded diagnostic summary rather than preserving a package `pass`
