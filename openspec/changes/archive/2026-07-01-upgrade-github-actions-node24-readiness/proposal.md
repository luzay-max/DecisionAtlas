## Why

The `mimo` branch CI now passes, but GitHub Actions reports Node.js 20 action deprecation warnings and warns about runner runtime migration. This should be converted from an ignored warning into an explicit release-readiness contract before the warnings become forced platform changes.

## What Changes

- Upgrade first-party and ecosystem GitHub Actions used by `.github/workflows/ci.yml` to Node 24-compatible major versions where available.
- Keep the workflow pinned to an explicit Windows runner image instead of relying on `windows-latest` redirection behavior.
- Preserve the existing validation scope: Node tests, typecheck, engine tests, benchmark fixture validation, and Playwright browser smoke flow.
- Add evidence that future CI runtime migration warnings are tracked as release-readiness issues.

## Capabilities

### New Capabilities

- `ci-runtime-readiness`: Defines CI runner and GitHub Action runtime compatibility expectations for release validation.

### Modified Capabilities

- None.

## Impact

- `.github/workflows/ci.yml`
- OpenSpec release-readiness documentation
- Project update log and CI evidence
