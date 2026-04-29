## Why

The v0.3 release-candidate documentation exists, but the repository still only has the older `v0.2.1` tag. Before starting v0.4 product-value work, the current v0.3 baseline needs a real, validated, pushed release-candidate tag so later changes have a stable comparison point.

## What Changes

- Re-run the canonical release gate for the current `main` baseline.
- Re-run OpenSpec strict validation so the release-candidate tag is backed by both implementation and spec validation.
- Update release-facing documentation to replace “tag not created yet” language with the actual v0.3 RC tag status once validation passes.
- Record the final validated commit, validation commands, and tag push result.
- Create and push the `v0.3.0-rc.1` tag after the release commit is clean and confirmed.
- Keep hosted preview and real-stack checks documented as confidence layers, not as replacements for the deterministic release gate.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `v0-3-release-candidate-baseline`: strengthen the RC baseline contract from “intended tag and tag-ready documentation” to “validated, created, and pushed RC tag with recorded final commit evidence.”
- `release-baseline-validation`: clarify that release-candidate validation must include post-documentation validation evidence and final tag status when a tag is actually created.

## Impact

- Affected documentation:
  - `docs/project/release-notes-v0.3.0-rc.1.md`
  - `docs/project/release-notes-v0.3.0-rc.1_zh-CN.md`
  - `docs/project/release-checklist.md`
  - `docs/project/2026-04-28-update-log.md` or a new update log entry if needed
  - `docs/plans/2026-04-29-decisionatlas-next-master-plan.md`
- Affected OpenSpec specs:
  - `openspec/specs/v0-3-release-candidate-baseline/spec.md`
  - `openspec/specs/release-baseline-validation/spec.md`
- Affected Git state:
  - create local tag `v0.3.0-rc.1`
  - push tag `v0.3.0-rc.1` to `origin`
- No product API, database schema, or runtime behavior changes are intended.
