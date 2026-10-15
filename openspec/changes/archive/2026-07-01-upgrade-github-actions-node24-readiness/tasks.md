## 1. Workflow Runtime Upgrade

- [x] 1.1 Update `.github/workflows/ci.yml` action references to Node 24-compatible major versions.
- [x] 1.2 Keep `runs-on: windows-2025` and preserve the existing CI validation step order.
- [x] 1.3 Add a project update log entry explaining the CI runtime readiness change.

## 2. Validation

- [x] 2.1 Run OpenSpec validation for the change and all specs.
- [x] 2.2 Run local workflow syntax-oriented checks for the changed YAML.
- [x] 2.3 Commit and push the branch, then verify the GitHub Actions run completes successfully.
- [x] 2.4 Confirm whether Node.js 20 deprecation warnings are resolved or document any remaining upstream warning.

## 3. Archive

- [x] 3.1 Sync the new `ci-runtime-readiness` spec into `openspec/specs`.
- [x] 3.2 Archive the OpenSpec change after implementation is complete.
