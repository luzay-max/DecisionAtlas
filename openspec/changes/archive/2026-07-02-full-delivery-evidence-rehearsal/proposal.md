## Why

DecisionAtlas can now generate release evidence, hosted readiness, benchmark comparison, external install evidence, real continuity rehearsal evidence, team handoff, and Code Decision Audit reports. The remaining gap is that durable readiness history only archives the older release/hosted/benchmark families, so a full delivery rehearsal is still split across `.tmp` files instead of one dated evidence record.

## What Changes

- Extend readiness evidence history to archive external install evidence, real backup/restore/upgrade rehearsal evidence, team handoff reports, and Code Decision Audit reports.
- Preserve missing evidence as `not_provided` and non-clean evidence as warning/blocking/operator-guided instead of treating omitted artifacts as pass.
- Update index/trend Markdown so the full delivery evidence state is visible at a glance.
- Update self-hosted delivery documentation with a command path for archiving the complete evidence bundle.
- Add tests and a smoke run proving the full evidence archive works from explicit JSON/Markdown inputs.

## Capabilities

### New Capabilities

- `full-delivery-evidence-rehearsal`: Defines the complete self-hosted delivery evidence archive flow across release, hosted, benchmark, external install, continuity, handoff, and audit artifacts.

### Modified Capabilities

- `readiness-evidence-history`: Add durable archive support for external install, real continuity, handoff, and audit evidence families.
- `self-hosted-delivery-rehearsal`: Require full evidence archive guidance before claiming a complete delivery rehearsal.

## Impact

- Updates to `scripts/ci/collect_readiness_evidence_history.py`.
- Tests for newly supported evidence families and index/trend output.
- Documentation updates for self-hosted delivery rehearsal and evidence history.
- Update log entry recording generated full delivery evidence archive smoke output.
