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

### Requirement: Completion taskbook reflects imported core-loop rehearsal
The completion taskbook SHALL update core-loop status when imported workspace core-loop evidence is added.

#### Scenario: Core-loop rehearsal is implemented
- **WHEN** imported workspace core-loop rehearsal is archived
- **THEN** the taskbook SHALL cite the collector, browser rehearsal, tests, and remaining evidence boundary.

#### Scenario: Core-loop evidence is still partial
- **WHEN** live import or multi-repo proof is still not complete
- **THEN** the taskbook SHALL keep the broader real GitHub repository validation line as partial.

### Requirement: Completion taskbook reflects multi-repo diagnosis rotation
The completion taskbook SHALL update real GitHub repository validation status when multi-repo diagnosis rotation exists.

#### Scenario: Multi-repo diagnosis is implemented
- **WHEN** multi-repo diagnosis rotation is archived
- **THEN** the taskbook SHALL cite the script, tests, smoke evidence, and remaining evidence boundary.

#### Scenario: Multi-repo diagnosis remains warning
- **WHEN** selected repositories produce warning or operator-guided results
- **THEN** the taskbook SHALL keep full product completion open and list the next quality or release-evidence step.

### Requirement: Completion taskbook reflects one-command release rehearsal
The completion taskbook SHALL update release evidence status when the one-command release rehearsal exists.

#### Scenario: One-command rehearsal is implemented
- **WHEN** the release rehearsal change is archived
- **THEN** the taskbook SHALL cite the script, tests, smoke output, and remaining evidence boundary.

#### Scenario: Release rehearsal remains warning
- **WHEN** the rehearsal produces warning because optional lanes are missing or non-clean
- **THEN** the taskbook SHALL keep full product completion open and list the next hardening item.

### Requirement: Completion taskbook reflects review audit UX hardening
The completion taskbook SHALL update team collaboration status after review/audit UX hardening exists.

#### Scenario: Review audit UX hardening is archived
- **WHEN** this change is archived
- **THEN** the taskbook SHALL cite UI changes, tests, browser evidence, and remaining external-host readiness work.

#### Scenario: External-host readiness remains incomplete
- **WHEN** review UX is hardened but external customer host evidence is still limited
- **THEN** the taskbook SHALL keep external customer host rehearsal as the next priority.

### Requirement: Completion taskbook reflects customer-host v2 rehearsal
The completion taskbook SHALL update external customer-host readiness after customer-host v2 rehearsal exists.

#### Scenario: Customer-host v2 rehearsal is archived
- **WHEN** this change is archived
- **THEN** the taskbook SHALL cite the collector, tests, smoke evidence, documentation, and remaining product-completion gaps.

#### Scenario: Customer-host v2 evidence remains operator-guided
- **WHEN** the rehearsal runs without a real customer-controlled host template
- **THEN** the taskbook SHALL preserve the remaining external-host limitation instead of marking the full product complete.

### Requirement: Completion taskbook reflects full-chain random repo release rehearsal
The completion taskbook SHALL update full-chain project status after full-chain random repository release rehearsal exists.

#### Scenario: Full-chain rehearsal is archived
- **WHEN** this change is archived
- **THEN** the taskbook SHALL cite the collector, random repo evidence, release/customer-host/browser evidence, tests, and remaining true customer-host boundary.

#### Scenario: Full-chain evidence is warning
- **WHEN** the rehearsal remains warning due to template, local-stack, provider, or operator-guided lanes
- **THEN** the taskbook SHALL keep final completion open and list the next real external trial action.

### Requirement: Completion taskbook references post-full-chain roadmap
The completion taskbook SHALL reference the post-full-chain product roadmap after it exists.

#### Scenario: Taskbook is updated
- **WHEN** the post-full-chain roadmap is created
- **THEN** the taskbook SHALL cite it and list the next evidence-gated actions.

#### Scenario: Full-chain evidence is warning
- **WHEN** the current full-chain evidence remains warning
- **THEN** the taskbook SHALL keep final completion open and SHALL NOT claim a clean customer-ready release.

### Requirement: Completion taskbook tracks real external host trial evidence
The project completion taskbook SHALL track real external host trial evidence as the next maturity checkpoint after full-chain random repo release rehearsal.

#### Scenario: Taskbook is updated
- **WHEN** real external host trial evidence support is implemented
- **THEN** the completion taskbook SHALL record what is complete, what evidence was generated, and what still requires a real external or customer-controlled machine.

#### Scenario: Only sample evidence exists
- **WHEN** the latest real external host trial evidence was generated from an example template or local-only smoke data
- **THEN** the taskbook SHALL keep the external customer proof boundary visible rather than marking customer-host validation fully complete.

### Requirement: Completion taskbook tracks pilot customer trial package
The project completion taskbook SHALL track the generated pilot customer trial package as the next step after real external host trial evidence gating.

#### Scenario: Trial package is implemented
- **WHEN** pilot customer trial package support is implemented
- **THEN** the taskbook SHALL cite the collector, generated package artifacts, tests, browser verification, and remaining real customer-machine boundary.

#### Scenario: Trial package remains warning
- **WHEN** the generated package contains warning, operator-guided, not-provided, or template-only evidence
- **THEN** the taskbook SHALL keep customer-ready completion open and SHALL NOT claim clean external pilot readiness.
