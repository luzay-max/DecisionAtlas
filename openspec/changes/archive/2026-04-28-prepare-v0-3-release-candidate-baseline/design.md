## Context

The previous roadmap has been executed through the v0.3 platform productization slices: login/scope switching, GitHub App installation binding, and private repository access binding are now available in the product. The repository also has a canonical release gate, hosted demo operator scripts, real-repository validation artifacts, and supported local stack startup commands.

This change is documentation- and validation-centered. It should freeze the current state as a release candidate rather than introduce new runtime behavior. Any code change should be limited to fixing a blocking mismatch discovered while validating the release candidate.

## Goals / Non-Goals

**Goals:**
- Establish `v0.3.0-rc.1` as the intended release-candidate baseline.
- Align release-facing docs around the current capability boundary.
- Record canonical validation evidence for the RC.
- Make limitations explicit so readers do not confuse the RC with a complete SaaS product.
- Preserve the distinction between default release validation and hosted/operator-guided validation.

**Non-Goals:**
- No new product surface.
- No new API or database model.
- No GitHub Marketplace/OAuth self-service installation flow.
- No secret vault or private credential rotation UI.
- No member-management or collaborative review workflow.
- No expansion of extraction, why, or drift logic.

## Decisions

### Treat v0.3 RC as a release baseline, not a feature sprint

The implementation should primarily update documentation, release notes, and validation records. This prevents scope creep after multiple platform productization slices and creates a stable reference point for later GitHub App sync operations, private access hardening, and hosted preview work.

Alternative considered: start directly on real-stack validation or GitHub App sync operations. Rejected because those tasks need a stable RC baseline to compare against.

### Keep pre-release as the canonical release gate

`scripts/ci/pre-release.ps1` remains the default local release gate. Hosted demo health/smoke checks and live real-repository validation remain operator-guided confidence layers, not required default gates.

Alternative considered: make hosted demo smoke or live repo validation mandatory for RC readiness. Rejected because the RC should stay reproducible locally without requiring external live credentials or hosted infrastructure.

### Document limitations as first-class release content

The RC documentation should explicitly state what is not present: full SaaS org management, secret vault, Marketplace/OAuth installation, billing, and multi-user collaborative review. That avoids over-claiming while still acknowledging platformized access flows.

Alternative considered: omit limitations from release notes and keep them only in roadmap docs. Rejected because release readers should not need to inspect planning documents to understand product boundaries.

## Risks / Trade-offs

- Docs could overstate platform maturity -> Mitigate by listing concrete limitations and supported operator paths.
- Validation could reveal a blocker -> Mitigate by pausing feature work and fixing only the blocker before tagging.
- Tag readiness could drift if commits land after validation -> Mitigate by recording the commit hash used for validation and preparing the tag only after docs and validation are final.
- Hosted preview could be confused with RC readiness -> Mitigate by keeping hosted preview as a later phase and documenting hosted checks as operator-guided.
