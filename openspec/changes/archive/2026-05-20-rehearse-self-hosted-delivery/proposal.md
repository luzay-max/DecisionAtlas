## Why

DecisionAtlas now has a self-hosted commercial baseline, readiness checklist, evidence history, and Code Decision Audit template, but the customer handoff path has not yet been exercised as one repeatable delivery rehearsal. The next risk is not missing SaaS features; it is claiming self-hosted readiness without a complete, dated evidence package that an operator can reproduce and explain.

## What Changes

- Add a self-hosted delivery rehearsal capability that defines how to run one end-to-end handoff rehearsal from startup/readiness checks through evidence capture.
- Require the rehearsal to preserve non-clean states such as `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` instead of converting them into pass.
- Connect the rehearsal to the existing self-hosted baseline, release evidence, hosted/operator readiness evidence, benchmark comparison evidence, readiness evidence history, and Code Decision Audit handoff.
- Add a customer/operator-facing rehearsal summary artifact that records what was tested, what evidence was produced, what was operator-guided, and what remains blocked or out of scope.
- Keep billing, hosted multi-tenancy, Marketplace/self-service OAuth, hosted secret vault, and runtime license enforcement out of scope.

## Capabilities

### New Capabilities

- `self-hosted-delivery-rehearsal`: Defines the repeatable self-hosted delivery rehearsal, required evidence families, state handling, and customer handoff summary expectations.

### Modified Capabilities

- `self-hosted-commercial-baseline`: Requires self-hosted customer handoff claims to reference a completed rehearsal or explicitly disclose why rehearsal evidence is missing.
- `readiness-evidence-history`: Allows readiness history entries to represent a self-hosted delivery rehearsal checkpoint and link the release, hosted/operator readiness, benchmark, and handoff summary artifacts.

## Impact

- Documentation and evidence workflow under `docs/project/`, `docs/evidence/readiness/`, and related release/readiness guidance.
- OpenSpec contracts for self-hosted commercial readiness and readiness evidence history.
- No new hosted SaaS control plane, billing, Marketplace integration, secret vault, or runtime license enforcement.
