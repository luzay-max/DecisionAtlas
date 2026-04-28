## 1. Release Baseline Audit

- [x] 1.1 Identify the current commit intended for `v0.3.0-rc.1` validation.
- [x] 1.2 Audit README, quick start, deployment, FAQ, release checklist, and existing release notes for outdated v0.2 or removed-script references.
- [x] 1.3 Confirm current supported startup and validation commands for demo stack, real stack, hosted operator checks, and pre-release validation.

## 2. Release Documentation

- [x] 2.1 Update README to describe the v0.3 RC stage and current productized platform flows.
- [x] 2.2 Update English and Chinese quick start / deployment / FAQ docs so startup paths, auth/scope, GitHub App binding, private repo binding, and limitations match.
- [x] 2.3 Add `v0.3.0-rc.1` release notes with shipped capabilities, validation evidence, known limitations, and intended tag readiness.
- [x] 2.4 Update the release checklist or release-facing docs with the canonical validation command and RC tag target.

## 3. Validation

- [x] 3.1 Run targeted documentation/link/script sanity checks for updated release-facing docs.
- [x] 3.2 Run `scripts/ci/pre-release.ps1` and record the result in release-facing notes.
- [x] 3.3 If validation fails, fix only blocking RC baseline issues and rerun the affected checks.

## 4. Tag Readiness

- [x] 4.1 Record the validated commit hash for `v0.3.0-rc.1`.
- [x] 4.2 Confirm no active OpenSpec changes or dirty working tree remain before tag preparation.
- [x] 4.3 Document the exact tag command for `v0.3.0-rc.1` without creating the tag unless explicitly requested.
