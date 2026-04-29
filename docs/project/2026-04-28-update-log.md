# 2026-04-28 Update Log

## Summary

- Advanced DecisionAtlas from v0.3 planning into a validated v0.3 release-candidate and hosted-preview readiness baseline.
- Completed the current v0.3 roadmap slices around release validation, real-stack validation, GitHub App sync operations, private repository access, and real-repository decision quality.
- Revalidated the running local product flow end to end across the primary demo surfaces.

## Completed Changes

### v0.3 release candidate baseline

- Prepared the v0.3 RC baseline documentation and release framing.
- Added v0.3 release notes in English and Chinese.
- Updated release readiness guidance so the current baseline can be validated through the canonical pre-release gate.
- Recorded v0.3 support boundaries and known limitations explicitly instead of implying production SaaS completeness.

### Real stack and hosted-preview readiness

- Added `docs/project/v0-3-real-stack-validation-report.md` to capture local real-stack validation evidence, command inventory, validation matrix, and remaining environment limitations.
- Added `docs/project/v0-3-hosted-preview-readiness-report.md` to separate hosted-preview confidence checks from the deterministic local release gate.
- Confirmed the current preview path is suitable for a guided external demo, while keeping live provider, hosted infra, and production multi-tenant claims out of scope.

### GitHub App and private repository operations

- Productized GitHub App sync operation surfaces enough for the v0.3 operator/admin path.
- Hardened private repository access handling and documented the supported token-backed access boundary.
- Kept credential handling conservative: tokens remain backend-facing and should not be exposed through browser-visible config, logs, screenshots, or shared reports.

### Real repository decision quality

- Improved the real-repository decision quality baseline and recorded current quality findings in `docs/project/real-repo-decision-quality-report.md`.
- Clarified that imported decision value depends on strong source refs, conversion diagnostics, and accepted-decision grounding.
- Kept why-search and drift behavior conservative when imported evidence is weak or only partially supported.

### Governance vision

- Captured the future AI governance knowledge-layer direction in `docs/visions/2026-04-27-ai-governance-knowledge-layer.md`.
- The vision frames user-uploaded Markdown standards, project decisions, error summaries, and development rules as machine-readable governance context.
- This remains a future direction after the v0.3 baseline, not part of the immediate RC scope.

## Validation

- OpenSpec validation was run during the v0.3 archive cycles and the main specs were kept synchronized.
- Final v0.3 RC pre-tag validation was run on 2026-04-29 09:32 +08:00:
  - `openspec validate --all --strict`: `34 passed, 0 failed`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1`: passed with exit code `0`
  - API tests: `25 passed`
  - web tests: `58 passed`
  - engine pytest: `167 passed`
  - Playwright smoke: `1 passed`
- The local browser full-chain check against the running project passed across:
  - home page
  - demo workspace dashboard
  - review page
  - decision detail navigation
  - why-search
  - timeline
  - drift
  - language toggle
  - advanced/experimental section anchor
- Browser console errors: none observed in the full-chain check.
- Page runtime errors: none observed in the full-chain check.
- The Playwright demo smoke test was updated to assert current product semantics rather than an older fixed database phase.
- Latest local E2E result:
  - `pnpm --filter @decisionatlas/web exec playwright test`
  - `1 passed`

## Current State

- `openspec list --json` showed no active changes after the latest archive cycles.
- The v0.3 roadmap has moved through release-candidate baseline, real-stack validation, hosted-preview readiness, GitHub App/private access hardening, and real-repository decision quality work.
- The product currently supports a coherent guided demo and a bounded real-repository analysis path, but it should still be described as a v0.3 RC / hosted-preview baseline rather than a production SaaS release.
- `v0.3.0-rc.1` is ready to tag after the `finalize-v0-3-rc-tag-and-validation` release commit is created and pushed.

## Notes For Next Work

- Keep using the v0.3 roadmap as the immediate source of truth for remaining polish.
- Treat real-repository quality, source-ref coverage, and why-search/drift precision as the highest-value next product improvements.
- Do not start the broader AI governance knowledge-layer implementation until the v0.3 baseline is stable enough to support it.
