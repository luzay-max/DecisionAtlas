# DecisionAtlas Release Notes: v0.2 Foundation Plus Current Quality Baseline

This document started as the `v0.2` release summary. It now also records the major quality slices that shipped after `v0.2` on the same product line, so it reflects the current `v0.2.1` branch baseline more accurately than the original v0.2-only notes.

## What v0.2 adds

- runtime selection between fake provider mode and OpenAI-compatible live provider mode
- configurable provider environment variables for extraction, retrieval, and semantic drift
- persisted GitHub import jobs with `full` and `since_last_sync` modes
- dashboard visibility into demo repo and latest import result
- demo-oriented homepage and review queue improvements
- deployment documentation for a public single-machine demo

## Quality slices shipped after v0.2

- existing imported workspaces can now be reopened or incrementally synced instead of always triggering a blind full rerun
- GitHub import transport failures are retried and classified more explicitly
- imported drift is more conservative and operationally clearer:
  - grouped weak follow-up alerts
  - tighter supersession boundaries
  - stale alert replacement during reevaluation
  - lower strong-signal false positives for maintenance-heavy fixes
- imported why-search is stronger:
  - better query rewrite for technical aliases
  - stronger hybrid retrieval weighting
  - chunk-backed supporting evidence
- imported workspaces now expose richer readiness:
  - review readiness
  - why readiness
  - drift readiness
  - recommended next actions
- indexing is now structure-aware:
  - structured chunking
  - bounded overlap
  - chunk metadata persisted for better supporting evidence ranking
- imported candidate conversion is stronger:
  - rationale-heavy imported docs use finer artifact-family routing
  - strong screened-in artifacts get one bounded recovery extraction attempt
  - imported summaries preserve final conversion diagnostics after the refined path runs
- release-quality packaging is clearer:
  - a canonical local pre-release script now acts as the branch baseline validation gate
  - offline benchmark fixture validation is part of that default release path
  - release-facing docs now distinguish the stable guided demo lane from optional imported real-repo validation more explicitly

## Supported in the current branch baseline

- one public demo workspace
- token-based GitHub import
- imported workspaces for public GitHub repositories
- citation-first why answers with support grading
- structured chunk-backed supporting evidence for imported why answers
- rule-first drift plus conservative semantic drift
- CI-safe fake provider fallback when live credentials are missing
- imported readiness surfaced in dashboard and search
- canonical local release baseline validation through `scripts/ci/pre-release.ps1`

## Known limits

- no GitHub App auth
- no private-repo access control
- no multi-user login or roles
- no multi-workspace SaaS flow
- semantic drift remains conservative and intentionally narrow
- imported real-repo outcomes can still be sparse or conversion-limited depending on repository signal quality
- drift remains manual, not continuous
- the seeded demo lane is still stronger as a presentation flow than the imported lane
- live real-repo smoke checks remain operator-guided validation, not part of the default offline release gate

## Deferred to v0.3

- GitHub App and webhook-based sync
- private repo support
- auth and permission layers
- multi-workspace operations
