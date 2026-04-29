## Context

DecisionAtlas already has v0.3 RC release notes, release checklist content, and archived OpenSpec work for the v0.3 platformization slices. The remaining gap is operational: the repository still has no `v0.3.0-rc.1` tag, so the release-candidate baseline is documented but not actually sealed in Git.

This change is intentionally narrow. It finalizes the release-candidate baseline through validation, documentation alignment, and Git tagging. It does not change runtime product behavior.

## Goals / Non-Goals

**Goals:**

- Revalidate the current release-candidate baseline after the latest documentation and E2E updates.
- Update release-facing documentation so the final validated commit and tag status are accurate.
- Create and push the `v0.3.0-rc.1` tag only after validation and a clean release commit.
- Preserve the distinction between mandatory canonical release validation and optional real-stack / hosted-preview confidence checks.

**Non-Goals:**

- No extraction, indexing, retrieval, drift, auth, GitHub App, or private-repo product behavior changes.
- No production SaaS claim, billing, organization admin, secret vault, or Marketplace/OAuth implementation.
- No attempt to make hosted-preview or live provider checks part of the deterministic release gate.

## Decisions

### Decision 1: Treat tagging as the implementation boundary

The implementation is complete only when the tag exists locally and on `origin`, not when the release notes merely say the tag is intended.

Alternative considered: leave release notes as tag-ready and let the operator tag manually later. This keeps ambiguity in the baseline and makes v0.4 comparison harder.

### Decision 2: Validate after documentation updates

The canonical release gate should run against the final release commit that includes the plan, release notes, OpenSpec artifacts, and any E2E updates that will be tagged.

Alternative considered: reuse the older pre-release result already recorded in the release notes. That result is useful historical evidence, but it does not validate the final tag target.

### Decision 3: Keep real-stack and hosted-preview checks as confidence layers

Docker, external hosted URLs, provider credentials, and private repository credentials are environment-dependent. They should remain explicitly documented as confidence layers unless the project later makes them deterministic enough for the default release gate.

Alternative considered: block the RC tag until every hosted/live lane is rerun. That would over-constrain the release candidate and blur deterministic release validation with operator-dependent validation.

## Risks / Trade-offs

- Risk: Validation takes longer or fails on an environment issue. Mitigation: classify failures as release-blocking only when they affect the canonical deterministic gate; keep environment-dependent checks documented separately.
- Risk: Tag is created on the wrong commit. Mitigation: record `git rev-parse --short HEAD` after validation and before tagging; verify `git show-ref --tags v0.3.0-rc.1` and remote tag state.
- Risk: Release notes drift from actual Git state. Mitigation: update English and Chinese release notes and the checklist in the same change that creates the tag.
- Risk: Existing uncommitted plan docs are accidentally omitted from the release baseline. Mitigation: include the new master plan in the release commit before validation/tagging if it remains part of the intended baseline.
