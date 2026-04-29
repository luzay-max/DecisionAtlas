## Context

DecisionAtlas already has repository document ingest, extracted candidate review, accepted decisions, grounded why-search, and OpenSpec-driven development history. The Stage 4 governance layer should reuse the same product philosophy: human-authored artifacts become structured, reviewable knowledge, and only human-accepted items become durable trust anchors.

This first slice is intentionally not an AI enforcement system. It creates the governance substrate that later diff checking and drift detection can read.

## Goals / Non-Goals

**Goals:**

- Store owner-scoped Markdown governance documents with stable metadata and source traceability.
- Classify documents using explicit user-provided types, with a bounded allowed type set.
- Extract reviewable rule drafts deterministically from Markdown structure.
- Let humans accept or reject rule drafts.
- Persist accepted governance rules with source document and source excerpt references.
- Add minimal API and UI surfaces for ingest, list, and review.

**Non-Goals:**

- No automatic CI blocking.
- No git diff governance checker in this slice.
- No LLM-only rule extraction requirement.
- No enterprise permission model beyond current owner/admin style boundaries.
- No complex knowledge graph UI.

## Decisions

### Decision: Use deterministic extraction first

Rule drafts will be extracted from headings, bullet lists, and explicit markers such as `Severity:` and `Scope:`. This keeps the first MVP deterministic, testable, and safe without requiring provider credentials.

Alternative considered: call an LLM during ingest to infer rules from arbitrary prose. That is useful later, but it would make review quality and tests provider-dependent too early.

### Decision: Separate documents, drafts, and accepted rules

Governance documents are source artifacts, rule drafts are review candidates, and accepted governance rules are the later checker input. This mirrors the existing candidate-to-accepted decision model and avoids treating every uploaded document sentence as enforceable truth.

Alternative considered: store only accepted rules and discard drafts. That loses auditability and makes it harder to explain why a rule exists.

### Decision: Keep status and severity bounded

Document type, document status, rule severity, rule scope, and draft review state will use bounded strings. Unknown values should be rejected or normalized into safe defaults instead of silently entering the governance layer.

Alternative considered: accept free-form values everywhere. That is flexible but would make future AI checks inconsistent and harder to trust.

### Decision: Minimal product surface over CLI-only

The MVP should have a small web surface because the product already has dashboard/review patterns and users need to inspect/accept/reject drafts. CLI and AI-callable checks can be added after accepted rules exist.

Alternative considered: CLI-only ingest. That is faster for developers but weaker for human review and traceability.

## Risks / Trade-offs

- Deterministic extraction may miss nuanced rules -> make the draft source visible and allow later LLM extraction as an enhancement.
- Uploaded Markdown may contain stale or conflicting rules -> require human review before rules become accepted.
- Governance scope can sprawl quickly -> restrict this change to single-project owner-scoped ingest and review.
- A governance UI could duplicate the decision review model -> keep the surface intentionally small and reuse existing visual patterns.

## Migration Plan

- Add database tables for governance documents and rule drafts.
- Add repositories and API routes.
- Add web client helpers and a minimal `/governance` page.
- Validate with deterministic fixtures and keep live AI/diff checks out of the default gate.
