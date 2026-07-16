# clean-self-hosted-install-rehearsal Specification

## Purpose
Define clean directory self-hosted install rehearsal evidence for DecisionAtlas operator/customer handoff readiness.
## Requirements
### Requirement: Clean install rehearsal generates bounded evidence
The system SHALL generate clean self-hosted install rehearsal evidence in both JSON and Markdown formats.

#### Scenario: Rehearsal evidence is generated
- **WHEN** an operator runs the clean install rehearsal with a package path, label, version label, and output path
- **THEN** the system SHALL write JSON and Markdown evidence containing schema version, generated timestamp, package identity, clean workspace path, source evidence paths, status summary, checks, blockers, limitations, and recommended next actions

#### Scenario: Markdown is operator-readable
- **WHEN** an operator opens the Markdown evidence without running the backend
- **THEN** the report SHALL expose the summary status, package path, clean workspace path, evidence family statuses, blockers, limitations, and rerun guidance as readable text

### Requirement: Rehearsal uses an isolated clean workspace
The system SHALL run package-level checks against an isolated clean workspace rather than the live development tree.

#### Scenario: Package is copied into scratch space
- **WHEN** the rehearsal starts with a package directory
- **THEN** the system SHALL copy the package into a label-scoped scratch directory before validating package contents
- **AND** it SHALL record both the original package path and clean package copy path

#### Scenario: Missing package is blocking
- **WHEN** the package path does not exist or cannot be copied
- **THEN** the system SHALL classify the rehearsal as `blocking` and identify the missing or unreadable package input

### Requirement: Rehearsal verifies operator handoff entry points
The system SHALL verify the copied package exposes the minimum operator handoff and runnable application entry points.

#### Scenario: Required package assets are present
- **WHEN** the copied package is inspected
- **THEN** the system SHALL check for package manifest, README, environment template, self-hosted package guide, operations runbook, readiness checklist, delivery rehearsal doc, license/support boundary doc, startup launcher, package verifier, dependency manifests and lockfiles, Docker Compose support, application runtime, engine runtime and migrations, prompts, and package browser smoke entry points

#### Scenario: Required asset is missing
- **WHEN** a required operator handoff or runnable runtime asset is absent from the copied package
- **THEN** the system SHALL mark that check `blocking` and include the missing relative path

### Requirement: Rehearsal preserves source evidence status
The system SHALL preserve pass and non-pass states from source evidence families.

#### Scenario: Evidence path is provided
- **WHEN** release evidence, hosted readiness, benchmark comparison, readiness history, package verification, public repository import, license boundary, or handoff report evidence is provided
- **THEN** the rehearsal SHALL read the evidence status when possible and record that family without converting non-pass states to pass

#### Scenario: Evidence path is missing
- **WHEN** an optional evidence family is not provided
- **THEN** the rehearsal SHALL mark that family `not_provided` or `operator_guided` with a rerun condition instead of omitting it

### Requirement: Rehearsal supports optional live stack probing
The system SHALL support optional live stack URL probing without requiring it for offline package structure checks.

#### Scenario: Live URLs are not provided
- **WHEN** API, web, or engine URLs are absent
- **THEN** the rehearsal SHALL mark live stack probing as `operator_guided` or `not_provided`
- **AND** it SHALL NOT claim live stack readiness

#### Scenario: Live probe fails
- **WHEN** a provided live URL cannot be reached
- **THEN** the rehearsal SHALL record `local_stack_failure` or `blocking` evidence with the failing URL and error summary

### Requirement: Rehearsal excludes premature hosted product commitments
The system SHALL keep clean install rehearsal scope aligned with the self-hosted commercial baseline.

#### Scenario: Deferred lanes are reported
- **WHEN** the rehearsal summarizes product readiness
- **THEN** it SHALL disclose that billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, online license server, and runtime license enforcement are not validated by this rehearsal

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
