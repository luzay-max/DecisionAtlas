## Context

Imported workspaces now have a clearer path from candidate review to the first accepted baseline, and the review queue exposes enough evidence for that acceptance step to be credible. The next weak spot is the imported why path after acceptance: `answer_why_question` already rewrites queries, searches accepted decisions, selects a primary decision, and supplements missing support with artifact chunks, but the support bundle is still narrow and can be brittle for technically equivalent questions.

The current implementation already has the building blocks this slice needs: accepted decisions, grounded source refs, artifact chunks with structural metadata, imported workspace readiness, and fixture-backed real-repo why benchmarks. This change should improve answer shaping and support assembly on top of those existing structures rather than introducing a new retrieval stack, new dependency, or schema migration.

## Goals / Non-Goals

**Goals:**

- Make imported why answers more stable for focused post-acceptance questions.
- Preserve one primary accepted decision as the answer anchor for focused questions.
- Upgrade more valid imported why answers from `limited_support` to `ok` when direct refs plus same-thread chunk support justify it.
- Keep weakly grounded post-acceptance questions explicitly bounded as `evidence_limited` instead of over-upgrading them.
- Extend curated benchmark protection for imported why regressions and stronger post-acceptance expectations.

**Non-Goals:**

- No new provider dependency, reranker service, or vector store change.
- No database migration or new persistence model for why answers.
- No rewrite of candidate extraction, review workflow, or drift evaluation.
- No broad product redesign of the search page beyond wording and status interpretation needed for the new behavior.

## Decisions

### 1. Evaluate imported why support as a support bundle centered on the primary accepted decision

For imported workspaces, support quality should not be derived from citation count alone. The engine should first establish one primary accepted decision, then evaluate a bounded support bundle around that decision using grounded source refs first and same-thread chunk evidence second.

This keeps the accepted decision as the trust anchor while allowing stronger imported answers to qualify for `ok` without requiring every supporting citation to come from direct source refs alone.

Alternative considered: keep the current rule that imported `ok` effectively depends on collecting two direct citations from accepted decisions. Rejected because it leaves technically valid accepted decisions stuck in `limited_support` when one strong direct quote and one structurally strong chunk are enough to justify a fuller answer.

### 2. Treat focused imported questions more conservatively than broad questions

Focused questions should stay on one primary accepted decision unless a secondary decision materially supports the same rationale thread. Broad questions may still expose supporting context, but focused imported answers should not become better-looking merely because nearby accepted decisions were also retrieved.

Alternative considered: allow supporting context whenever multiple accepted decisions are retrieved above a score threshold. Rejected because it can make weak focused answers look stronger than they are and blurs the answer anchor.

### 3. Use query-equivalence handling to stabilize retrieval before support grading

This slice should improve support quality by making technically equivalent phrasings more likely to select the same accepted decision before citation assembly begins. Query rewrite, lexical overlap, and semantic retrieval should work together, but none of them should broaden the question into a generic topic query.

Alternative considered: solve support quality only by adding more supporting chunk citations after retrieval. Rejected because a wrong primary decision with richer citations is still the wrong answer.

### 4. Protect imported why improvements with curated benchmark expectations, not exact prose snapshots

The benchmark layer should express bounded expectations such as expected why status families, minimum citations, accepted-baseline prerequisites, and equivalent-phrasing cases. It should not require exact answer text.

This matches the product goal: improve reliability and support grading without freezing incidental wording.

## Risks / Trade-offs

- Stronger chunk-backed upgrades may over-credit weak supporting text -> require same-thread relevance and keep accepted decisions as the anchor.
- More conservative focused-answer shaping may reduce visible supporting context -> only broad questions should gain secondary context by default.
- Equivalent-query handling may drift into broader topic normalization -> keep normalization scoped to technical aliases and preserve specific decision intent.
- More benchmark protection increases maintenance overhead -> use a small curated case set instead of large answer snapshots.

## Migration Plan

1. Tighten imported why-answer selection and support grading in engine retrieval logic and tests.
2. Update API and frontend expectations for any changed imported why statuses or next-action guidance.
3. Extend benchmark fixtures and fixture tests for the protected imported why cases.
4. Run targeted why tests, fixture validation, and the canonical pre-release gate before shipping.

## Open Questions

- Should the first version of equivalent-question protection add only new benchmark cases for `browser-use`, or also require a second curated repository immediately?
- Should imported `limited_support` expose more machine-readable support diagnostics in the API now, or is status plus citations sufficient for this slice?
