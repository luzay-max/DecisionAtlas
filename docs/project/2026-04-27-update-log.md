# 2026-04-27 Update Log

## Summary

- Productized the remaining v0.3 platform access flows and pushed them to `main`.
- Cleaned obsolete local development scripts that had been superseded by the current stack runners and release gate.
- Reduced local browser console noise in the demo/real stack startup path.

## Completed Changes

### Private repository access product flow

- Added an admin-only private repository access panel for binding token-backed GitHub access inside the current owner scope.
- Reused the existing `/imports/github/private-access/bind` API instead of introducing a new credential model.
- Kept owner scope session-derived and avoided rendering submitted token material after success or failure.
- Synced and archived `productize-private-repo-access`.
- Pushed commit `4275be6 feat: productize private repo access`.

### Script cleanup

- Removed obsolete early development scripts:
  - `scripts/dev/up.ps1`
  - `scripts/dev/prepare-demo.ps1`
  - `scripts/ci/run_demo_smoke.ps1`
- Removed generated Python cache under `scripts/ci/__pycache__`.
- Kept the current supported entry points:
  - `scripts/dev/start-real-stack.bat`
  - `scripts/dev/start-real-stack.ps1`
  - `scripts/dev/stop-real-stack.bat`
  - `scripts/dev/stop-real-stack.ps1`
  - `scripts/dev/start-demo-stack.ps1`
  - `scripts/dev/stop-demo-stack.ps1`
  - `scripts/ci/pre-release.ps1`
  - `scripts/ci/start-engine-smoke.ps1`
  - `scripts/ci/start-api-smoke.ps1`
  - `scripts/ci/start-web-smoke.ps1`
  - `scripts/demo/*.ps1`

### Local stack polish

- Added a favicon endpoint and icon asset so `/favicon.ico` no longer 404s.
- Aligned the web default API base URL to `http://127.0.0.1:3001`.
- Set `AUTO_BOOTSTRAP_AUTH=true` in local demo, real stack, and smoke API startup scripts so restarted local stacks recover a bootstrap session without a visible `/auth/session` 401.

## Validation

- `./scripts/ci/pre-release.ps1` passed after private access productization:
  - web tests: 55 passed
  - API tests: 25 passed
  - engine pytest: 162 passed
  - Playwright demo smoke: 1 passed
- After script cleanup and local stack polish:
  - PowerShell script parse check passed
  - `pnpm --filter @decisionatlas/web typecheck` passed
  - `pnpm --filter @decisionatlas/api test -- auth-route` passed, 4 tests
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1 -SkipDependencyChecks` passed
  - `pnpm --filter @decisionatlas/web exec playwright test tests-e2e/demo-smoke.spec.ts --reporter=line` passed, 1 test
  - `/favicon.ico` returned 200 on the local running web server

## Operational Notes

- The supported real-stack startup command is `.\scripts\dev\start-real-stack.bat` or `pnpm dev:real`.
- The API process must be restarted for `AUTO_BOOTSTRAP_AUTH=true` startup changes to affect an already-running local stack.
- OpenSpec active changes were empty after archiving the private access product flow.
