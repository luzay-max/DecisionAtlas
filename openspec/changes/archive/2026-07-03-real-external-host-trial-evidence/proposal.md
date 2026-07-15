## Why

The current customer-host evidence pipeline can prove that the collector works, but a filled example template can still look too close to a successful external trial. Before claiming customer-ready delivery, DecisionAtlas needs an explicit evidence gate that separates real customer-controlled host proof from local smoke runs, templates, placeholders, and operator-guided evidence.

## What Changes

- Add a real external host trial evidence collector that composes customer-host v2 evidence, full-chain random repo evidence, and sanitized host input into one customer-safe gate.
- Detect placeholder/template values such as `fill-me`, `customer-or-operator-name`, `optional`, sample limitations, and local-only proof.
- Preserve source statuses from customer-host v2 and full-chain evidence instead of converting warnings into pass.
- Add durable readiness history support for the new evidence family.
- Add tests and documentation that show sample/template evidence remains warning/operator-guided, while properly sanitized external host evidence can pass.

## Capabilities

### New Capabilities
- `real-external-host-trial-evidence`: Validates and summarizes whether external/customer-controlled host trial evidence is strong enough for release or customer handoff claims.

### Modified Capabilities
- `readiness-evidence-history`: Adds a first-class family for real external host trial evidence and exposes it in index/trend output.
- `external-customer-host-rehearsal-v2`: Clarifies that customer-host v2 evidence must feed the stricter real external host trial gate before external trial claims.
- `full-chain-random-repo-release-rehearsal`: Clarifies that full-chain evidence can be composed into the real external host trial gate without hiding warning lanes.
- `project-completion-taskbook`: Updates the completion taskbook with the new external host trial evidence step and its remaining boundary.

## Impact

- Affected code: `scripts/ci/`, `services/engine/tests/ci/`.
- Affected docs: `docs/project/`, `docs/plans/`, OpenSpec specs.
- Affected evidence: `.tmp/real-external-host-trial-evidence.json/md`, optional `docs/evidence/readiness/*real-external-host-trial-evidence*/`.
- No breaking API or schema change for existing collectors; this adds a stricter aggregation and validation layer.
