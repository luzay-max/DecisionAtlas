# self-hosted-delivery-rehearsal Specification

## Purpose
Defines a repeatable self-hosted delivery rehearsal workflow that produces customer-readable handoff evidence covering package verification, clean install, and continuity readiness before claiming operator trial readiness.
## Requirements
### Requirement: Self-hosted delivery rehearsal is repeatable
The system SHALL define a repeatable self-hosted delivery rehearsal that an operator can run before claiming customer handoff readiness.

#### Scenario: Operator starts a rehearsal
- **WHEN** an operator prepares a self-hosted delivery rehearsal
- **THEN** the rehearsal guidance SHALL identify the rehearsal label, target deployment mode, relevant commit or version label, evidence output paths, and required validation commands.

#### Scenario: Rehearsal uses existing baseline commands
- **WHEN** the rehearsal describes validation steps
- **THEN** it SHALL reference existing startup, health, OpenSpec strict validation, governance guardrail, release evidence, hosted/operator readiness, benchmark comparison, and readiness history commands where applicable.

### Requirement: Rehearsal evidence preserves non-clean states
The system SHALL preserve non-clean evidence states during self-hosted delivery rehearsal reporting.

#### Scenario: Evidence is not clean pass
- **WHEN** a rehearsal produces `warning`, `blocking`, `operator_guided`, `known_limitation`, or `not_provided` evidence
- **THEN** the rehearsal summary SHALL disclose that state
- **AND** it SHALL NOT present the affected lane as pass.

#### Scenario: Live inputs are absent
- **WHEN** hosted URLs, provider credentials, private repository credentials, or live benchmark inputs are unavailable
- **THEN** the rehearsal SHALL record an explicit operator-guided, known-limitation, not-provided, or blocking state with the rerun condition.

### Requirement: Rehearsal creates customer-readable handoff evidence
The system SHALL produce or require a customer/operator-readable rehearsal summary for self-hosted delivery.

#### Scenario: Rehearsal summary is prepared
- **WHEN** a rehearsal is completed or paused
- **THEN** the summary SHALL list tested scope, deployment mode, commands run, generated evidence artifacts, archived readiness history entry, limitations, and recommended next actions.

#### Scenario: Paid pilot handoff is prepared
- **WHEN** the rehearsal is used for a paid pilot or customer evaluation
- **THEN** the handoff SHALL reference the Code Decision Audit template or an equivalent report
- **AND** it SHALL include evidence statuses, drift/why-search readiness, benchmark comparison status, and limitations.

### Requirement: Rehearsal excludes premature SaaS commitments
The system SHALL keep self-hosted delivery rehearsal scope aligned with the self-hosted commercial baseline.

#### Scenario: Scope is documented
- **WHEN** the rehearsal describes product readiness
- **THEN** it SHALL state that billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, managed hosted service operations, and runtime license enforcement are not validated by this rehearsal.

### Requirement: Rehearsal includes package verification evidence
The self-hosted delivery rehearsal SHALL include self-hosted package verification evidence before claiming package handoff readiness.

#### Scenario: Package verification is available
- **WHEN** a self-hosted delivery rehearsal claims a package is ready for operator handoff
- **THEN** the rehearsal SHALL reference package manifest path, package verification JSON/Markdown, package status, and any blocking or operator-guided lanes

#### Scenario: Package verification is missing
- **WHEN** a self-hosted delivery rehearsal is completed without package verification evidence
- **THEN** the rehearsal SHALL classify package handoff readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim clean offline package readiness

#### Scenario: Package verification has warnings
- **WHEN** package verification reports `warning`, `blocking`, `operator_guided`, `known_limitation`, or `not_provided`
- **THEN** the rehearsal summary SHALL preserve those states and list the required follow-up before customer handoff

### Requirement: Delivery rehearsal includes clean install evidence
The self-hosted delivery rehearsal SHALL include clean install rehearsal evidence before claiming external operator trial readiness.

#### Scenario: Clean install evidence is available
- **WHEN** a self-hosted delivery rehearsal claims external operator trial readiness
- **THEN** the rehearsal summary SHALL reference clean install rehearsal JSON/Markdown, clean package copy path, package verification status, evidence family statuses, and any blockers or operator-guided lanes

#### Scenario: Clean install evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without clean install rehearsal evidence
- **THEN** the rehearsal SHALL classify external operator trial readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that the package has been validated in a clean install flow

### Requirement: Self-hosted delivery rehearsal includes continuity evidence
The self-hosted delivery rehearsal SHALL include backup/restore/upgrade rehearsal evidence before claiming customer trial or paid handoff continuity readiness.

#### Scenario: Continuity evidence is available
- **WHEN** self-hosted delivery rehearsal evidence is prepared for customer handoff
- **THEN** it SHALL reference backup/restore/upgrade rehearsal JSON or Markdown evidence.

#### Scenario: Continuity evidence is missing
- **WHEN** backup/restore/upgrade rehearsal evidence is absent
- **THEN** delivery rehearsal material SHALL preserve `operator_guided` or `not_provided` state and avoid claiming clean continuity readiness.

### Requirement: Delivery rehearsal references external install evidence
The self-hosted delivery rehearsal SHALL include external install evidence before claiming customer-controlled host install readiness.

#### Scenario: External install evidence is available
- **WHEN** a self-hosted delivery rehearsal claims customer-controlled host install readiness
- **THEN** the rehearsal summary SHALL reference external install evidence JSON or Markdown, external host class, package identity, lane statuses, blockers, and limitations

#### Scenario: External install evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without external install evidence
- **THEN** the rehearsal SHALL classify customer-controlled host install readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that the package has been validated on a non-developer or customer-controlled machine

### Requirement: Delivery rehearsal references real continuity evidence
The self-hosted delivery rehearsal SHALL reference real backup/restore/upgrade rehearsal evidence before claiming tested continuity readiness.

#### Scenario: Real continuity evidence is supplied
- **WHEN** a self-hosted delivery rehearsal claims tested backup, restore, upgrade, or rollback readiness
- **THEN** the rehearsal SHALL reference real continuity evidence JSON or Markdown, scratch scope, restore validation status, post-upgrade status, rollback plan status, blockers, and limitations

#### Scenario: Real continuity evidence is missing
- **WHEN** a self-hosted delivery rehearsal is completed without real continuity rehearsal evidence
- **THEN** the rehearsal SHALL classify tested continuity readiness as `not_provided` or `operator_guided`
- **AND** it SHALL NOT claim that backup, restore, upgrade, or rollback mechanics have been exercised

### Requirement: Delivery rehearsal archives complete evidence history
The self-hosted delivery rehearsal SHALL include guidance for archiving complete delivery evidence into readiness history.

#### Scenario: Complete evidence is available
- **WHEN** release, hosted, benchmark, external install, real continuity, handoff, and audit evidence artifacts exist
- **THEN** the rehearsal documentation SHALL provide a command that archives those artifacts into readiness history and regenerates index/trend output.

#### Scenario: Evidence is incomplete
- **WHEN** some complete delivery evidence artifacts are missing
- **THEN** the rehearsal guidance SHALL require the archive to preserve missing evidence as `not_provided`, `operator_guided`, `warning`, or `blocking`.

### Requirement: Delivery rehearsal references customer-host v2 evidence
Self-hosted delivery rehearsal material SHALL reference customer-host v2 evidence before claiming customer-controlled host readiness.

#### Scenario: Customer-host v2 evidence exists
- **WHEN** delivery rehearsal or handoff material claims customer-controlled host readiness
- **THEN** it SHALL reference customer-host v2 JSON or Markdown evidence, host proof level, lane statuses, blockers, and limitations.

#### Scenario: Customer-host v2 evidence is missing
- **WHEN** customer-host v2 evidence is absent
- **THEN** delivery rehearsal or handoff material SHALL preserve `not_provided` or `operator_guided` state and SHALL NOT claim verified external customer-host readiness.
