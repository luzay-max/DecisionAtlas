## Context

The `mimo` branch CI is green, but GitHub Actions reports Node.js 20 action deprecation warnings. The workflow already pins `windows-2025` and sets `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`, so the remaining risk is that several action references are still on old major versions that target older JavaScript runtimes.

## Goals / Non-Goals

**Goals:**

- Upgrade the workflow's GitHub Action references to current Node 24-compatible major versions where available.
- Preserve the existing validation sequence and avoid changing product behavior.
- Keep the runner pinned to an explicit Windows image.
- Record the change as release-readiness work with OpenSpec traceability.

**Non-Goals:**

- Add Linux/macOS matrix coverage.
- Change application code or test behavior.
- Introduce new CI jobs, deployment automation, or release publishing.
- Solve unrelated GitHub platform notices outside this repository workflow.

## Decisions

- Keep `runs-on: windows-2025` instead of `windows-latest`.
  - Rationale: the warning about `windows-latest` redirection is avoided by explicit pinning, and the existing workflow already made that correct choice.
  - Alternative considered: switch back to `windows-latest`; rejected because alias migration would reintroduce uncertainty.

- Upgrade action major versions in place.
  - Rationale: this is the smallest change that addresses the deprecation warning without changing the workflow shape.
  - Alternative considered: keep old action majors and rely on `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`; rejected because it leaves a recurring warning and depends on compatibility shims.

- Keep the validation steps unchanged.
  - Rationale: current CI already covers Node tests, typecheck, engine tests, benchmark validation, and browser smoke; runtime readiness should not broaden the functional test scope.

## Risks / Trade-offs

- Action major-version upgrades can contain breaking behavior -> Mitigate by running the full GitHub Actions workflow after push.
- New action majors may require newer runner versions -> Mitigate by using GitHub-hosted `windows-2025`, which tracks supported runner versions.
- External actions may continue to emit upstream warnings -> Mitigate by treating remaining warnings as evidence for a follow-up change instead of hiding them locally.
