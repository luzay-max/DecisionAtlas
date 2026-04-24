## Why

Imported workspaces can now produce reviewable candidates and expose readiness, but the review queue still shows sparse decision fields that force reviewers to open detail pages before deciding whether to accept or reject. The next focused product slice is to make candidate review itself more trustworthy and faster, so a first accepted imported baseline is easier to establish.

## What Changes

- Improve imported candidate cards with stronger evidence summaries, source-ref previews, provenance, confidence interpretation, and extraction/funnel context where available.
- Make the review page explain why accepting a strong imported candidate matters for first accepted baseline, why-search, and drift.
- Keep review actions simple: accept, reject, supersede remain the workflow; no multi-user approval system or extraction rewrite.
- Add API/frontend tests that protect imported review-card evidence and first-baseline guidance.
- Keep demo review behavior stable while making imported review more informative.

## Capabilities

### New Capabilities

- `imported-review-decision-quality`: covers imported candidate review cards, evidence summaries, provenance indicators, and first-baseline review guidance.

### Modified Capabilities

- `source-ref-coverage`: review surfaces should expose enough source-ref coverage information for reviewers to understand whether a candidate is well grounded or thinly supported.
- `real-repository-outcomes`: imported review should make the path from review-ready to first accepted baseline clearer and connect accepted candidates to downstream why/drift readiness.

## Impact

- Affected backend/API: `services/engine/app/api/decisions.py`, repositories used for source refs/artifacts, and decision API tests.
- Affected frontend: `apps/web/lib/api.ts`, `apps/web/components/review/*`, i18n messages, and review component tests.
- Affected docs/specs: OpenSpec specs for imported review quality and related source-ref/readiness behavior.
- Dependencies: no new external dependencies or database migration expected; use existing decisions, source refs, artifacts, and import summary fields.
