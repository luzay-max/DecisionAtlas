## Context

Imported real-repo work has improved around candidate conversion, readiness, why support, and validation. The remaining user-facing gap is the review queue: imported candidates are sorted by confidence, but reviewers only see generic decision fields and often need to open detail pages to inspect evidence before accepting the first baseline decision.

The existing backend already stores decisions, source refs, artifacts, provenance, confidence, and import summaries. This change should reuse those structures and enrich the review queue read model and UI, not introduce a new workflow or database migration.

## Goals / Non-Goals

**Goals:**

- Make imported candidate cards easier to judge directly from the review queue.
- Surface source-ref coverage and short evidence previews for each candidate.
- Show artifact provenance such as source type, title, URL, and repository context where available.
- Explain that accepting a strong imported candidate establishes the first baseline that downstream why/drift can use.
- Preserve the existing accept/reject/supersede review actions.

**Non-Goals:**

- No multi-reviewer approval, comments, assignments, or audit workflow.
- No extraction prompt rewrite or candidate generation algorithm change.
- No database migration unless implementation proves existing fields cannot support the read model.
- No private repo, auth UI, or hosted demo scope.

## Decisions

### 1. Enrich the existing decisions list endpoint

`GET /decisions?workspace_slug=...&review_state=candidate` should return optional review-support fields for list cards, including source-ref count, evidence preview, and artifact summary. This avoids forcing the frontend to make one detail request per candidate.

Alternative considered: fetch decision details for every candidate from the review page. Rejected because it would multiply API requests and make review queue latency scale poorly.

### 2. Keep review-support fields optional and backward-compatible

The frontend should treat new fields as optional. Demo candidates and older records may not have full provenance or source-ref coverage. The UI should degrade gracefully and still show the core decision fields.

### 3. Use source refs as evidence previews, not final truth claims

The review card should show short quotes and coverage counts as evidence for reviewer judgment. It should not imply the system has already accepted the decision or that downstream why-search is fully trustworthy before human acceptance.

### 4. Separate imported guidance from demo guidance

The seeded demo lane should keep its stable guided narrative. Imported workspaces should receive review-specific guidance about first accepted baseline, source evidence, and downstream why/drift readiness.

## Risks / Trade-offs

- Review cards may become noisy -> limit preview count and keep detail page available for full evidence.
- Some candidates have thin source-ref coverage -> show that directly rather than hiding it.
- API payload grows -> include compact summaries, not full artifact content.
- Confidence may be overread as correctness -> pair confidence with evidence coverage and provenance language.

## Migration Plan

1. Add backend serialization for compact review evidence and artifact summaries.
2. Extend API tests for candidate list evidence payloads and graceful thin-coverage cases.
3. Extend web types and review card rendering.
4. Add frontend tests for imported review quality signals and demo-lane stability.
5. Run targeted backend/frontend tests, then the canonical pre-release gate if the change is ready to ship.
