## 1. Align release-facing documentation

- [x] 1.1 Update README and README_zh-CN current-stage wording so the project describes the post-v0.2.1 imported-readiness baseline rather than only v0.2 demo hardening.
- [x] 1.2 Review quick start, FAQ, demo script, release checklist, and real-repository validation docs for mismatched release commands, lane boundaries, and limitation wording.
- [x] 1.3 Add v0.2.2 release notes that summarize shipped capabilities, supported scope, validation path, and remaining limitations.

## 2. Validate the release baseline

- [x] 2.1 Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/pre-release.ps1` and capture the result.
- [x] 2.2 If the canonical gate exposes a release-blocking mismatch in docs, scripts, or smoke coverage, fix the smallest scoped issue and rerun the relevant validation.
- [x] 2.3 Record the canonical validation result in the v0.2.2 release notes or release checklist.

## 3. Prepare the version point

- [x] 3.1 Confirm the intended v0.2.2 tag target commit after validation passes.
- [x] 3.2 Confirm the working tree contains only release-baseline documentation, validation, and OpenSpec archive changes before tagging.
- [x] 3.3 Prepare tag instructions or create the `v0.2.2` tag after explicit release confirmation, then record the final tag status.
