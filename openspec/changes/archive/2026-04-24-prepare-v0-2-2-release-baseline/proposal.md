## Why

Recent work materially changed the current baseline: release validation is now canonical, imported candidate conversion is stronger, imported review readiness has first-accepted-baseline semantics, Playwright smoke coverage was repaired, and English/Chinese docs were separated. The project needs a focused release-baseline change so the current `main` state can become a clear `v0.2.2` milestone before the next live real-repo validation work begins.

## What Changes

- Update release-facing documentation so the current project stage describes the post-`v0.2.1` imported-readiness baseline rather than the older v0.2 demo-hardening state.
- Add `v0.2.2` release notes that summarize shipped capabilities, validation commands, supported scope, and remaining limitations.
- Ensure English and Chinese release-facing docs agree on current capabilities, lane boundaries, and limitations.
- Run the canonical release baseline validation path and record the result in the release checklist or release notes.
- Prepare the repository for a `v0.2.2` tag after validation passes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `release-baseline-validation`: Extend the release baseline contract so a release-style milestone includes version-facing documentation, current-stage wording, canonical validation evidence, and tag readiness.

## Impact

- Documentation: `README.md`, `README_zh-CN.md`, `docs/project/*`, release notes, release checklist, and planning docs as needed.
- Validation: `scripts/ci/pre-release.ps1` remains the canonical gate and may be updated only if release documentation exposes a mismatch.
- Release process: the change prepares, but does not automatically require, creating and pushing a `v0.2.2` tag after validation.
