## 1. Rehearsal Scope

- [x] 1.1 Review the self-hosted commercial baseline, readiness checklist, release checklist, readiness evidence history, and Code Decision Audit template before changing implementation docs.
- [x] 1.2 Define the rehearsal label, target deployment mode, evidence output paths, and pass/warning/operator-guided classification rules.
- [x] 1.3 Classify each rehearsal lane as required, optional, or operator-guided when hosted URLs, provider credentials, private repository credentials, or live benchmark inputs are absent.

## 2. Rehearsal Execution

- [x] 2.1 Run or document the self-hosted startup and service health path for the current environment.
- [x] 2.2 Run OpenSpec strict validation and governance guardrail summary.
- [x] 2.3 Run the canonical pre-release baseline or record the blocker and accepted substitute evidence.
- [x] 2.4 Generate release evidence JSON/Markdown and hosted/operator readiness JSON/Markdown.
- [x] 2.5 Generate, reuse, or explicitly mark benchmark comparison evidence with source paths and state classification.
- [x] 2.6 Archive selected release, hosted readiness, and benchmark artifacts into readiness evidence history.

## 3. Customer Handoff

- [x] 3.1 Produce a self-hosted delivery rehearsal summary under durable documentation or evidence paths.
- [x] 3.2 Prepare a sample Code Decision Audit handoff from the generated evidence.
- [x] 3.3 Record limitations, non-clean states, missing optional inputs, rerun conditions, and recommended next actions.

## 4. Documentation Updates

- [x] 4.1 Update self-hosted baseline and readiness docs to reference the rehearsal process.
- [x] 4.2 Update release checklist or readiness evidence guidance if the rehearsal introduces new durable evidence conventions.
- [x] 4.3 Ensure docs keep billing, hosted multi-tenancy, Marketplace/self-service OAuth, hosted secret vault, managed hosted service operations, and runtime license enforcement out of scope.

## 5. Validation

- [x] 5.1 Run local Markdown/link sanity checks for touched docs where available.
- [x] 5.2 Run `openspec validate rehearse-self-hosted-delivery --type change --strict`.
- [x] 5.3 Run `openspec validate --all --strict`.
