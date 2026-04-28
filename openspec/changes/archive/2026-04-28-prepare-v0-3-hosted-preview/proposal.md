## Why

v0.3 RC now has release baseline, real-stack validation, GitHub App sync operations, private repo access hardening, and real-repo decision quality improvements. The next risk is whether this baseline can be presented as an externally hosted preview with a repeatable operator checklist, recovery path, and clear public-demo boundaries.

## What Changes

- Prepare a hosted preview readiness slice that turns the current v0.3 RC into a checklist-driven external demo candidate.
- Add or tighten hosted preview documentation for environment readiness, health/smoke checks, demo reset/reseed rehearsal, and incident recovery.
- Define a public walkthrough script that keeps the seeded demo lane stable while explaining imported real-repo and platform access lanes as bounded operator/admin capabilities.
- Record a hosted preview readiness report with commands, observed results, pass/fail status, known limitations, and required follow-ups.
- Keep the scope bounded: do not build production SaaS infrastructure, billing, organization management, a secret vault, or unlimited public repository import.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `hosted-demo-operator-flow`: Require hosted preview readiness to include a public-demo checklist, recovery drill evidence, and external walkthrough boundaries.
- `v0-3-real-stack-validation`: Require validation reports to distinguish local RC confidence from externally hosted preview readiness and record hosted-preview checks when available.
- `release-baseline-validation`: Require release-facing docs to identify hosted preview readiness as a post-RC confidence layer rather than a replacement for the canonical release gate.
- `guided-demo-experience`: Require the guided demo to remain the stable public walkthrough lane during hosted preview, with imported lanes presented as optional bounded demonstrations.

## Impact

- Documentation under `docs/project`, especially hosted operator guide, deployment/quick start links, demo script, and v0.3 validation reports.
- Demo scripts and operator check commands under `scripts/demo` only if gaps are found during readiness verification.
- Web-facing copy only if the existing guided demo or imported-lane boundary is unclear for external preview use.
- OpenSpec specs and archived change artifacts for the hosted preview readiness contract.
