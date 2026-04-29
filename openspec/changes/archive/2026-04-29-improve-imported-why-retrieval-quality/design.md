## Context

DecisionAtlas now has a stable v0.3 RC baseline and a stronger imported candidate quality model. The next value bottleneck is whether an accepted imported decision can be found and supported when a user asks the same rationale in different wording.

The current engine already has several useful primitives: query rewriting, significant-term filtering, hybrid full-text/vector retrieval, accepted-decision anchoring, source refs, artifact chunks with structural metadata, and conservative imported answer states. This change should improve calibration and coverage around those primitives rather than introducing a new free-form answering model.

## Goals / Non-Goals

**Goals:**

- Improve recall for technically equivalent imported why-questions.
- Keep accepted decisions as the trust anchor for imported why answers.
- Let semantic retrieval contribute materially when exact wording differs.
- Use same-thread artifact chunks to strengthen support when direct source refs are thin.
- Preserve explicit support states: `ok`, `limited_support`, `evidence_limited`, and `review_required`.
- Add deterministic tests and benchmark cases for equivalent phrasing, neighboring decisions, and weak evidence.

**Non-Goals:**

- Do not answer imported why-questions directly from raw artifact chunks without an accepted decision anchor.
- Do not use a free-form LLM judge to decide support state.
- Do not make why-search cross-workspace or cross-repository.
- Do not broaden live provider validation into default CI.
- Do not rewrite the extraction pipeline in this slice.

## Decisions

### Decision 1: Extend deterministic query normalization before changing answer generation

The first layer should normalize common technical aliases and equivalent phrases before retrieval, for example identity/token variants, HTTP/download phrasing, queue/background-job phrasing, and release-candidate branch wording. This keeps the change testable and directly addresses known imported why misses.

Alternative considered: rely entirely on vector search for synonym recall. Rejected because embedding behavior is harder to bound in default tests, and lexical normalization gives deterministic coverage for known product vocabulary.

### Decision 2: Rebalance hybrid retrieval without removing lexical safeguards

Semantic retrieval should be strong enough to rescue equivalent wording, but lexical and source-ref fit should still prevent drift to nearby accepted decisions. The implementation should tune weighting and ranking with tests that include a plausible weaker lexical neighbor.

Alternative considered: heavily prioritize vector score. Rejected because imported workspaces often contain adjacent decisions with overlapping vocabulary; a pure semantic boost can select a related but wrong rationale.

### Decision 3: Use artifact chunks only as support for the selected accepted decision

Chunk retrieval should run after a primary accepted decision is selected and should be limited to artifacts/source refs tied to that decision or the same rationale thread. Chunk citations can upgrade support only when they reinforce the accepted decision; they must not become an independent answer source.

Alternative considered: retrieve chunks globally first and answer from the best chunks. Rejected because that weakens the accepted-decision trust boundary and could bypass review.

### Decision 4: Keep support grading deterministic

Support state should be based on accepted baseline availability, primary-decision match strength, direct citation count, same-thread chunk support, and bounded quality signals. The API can expose additional answer context if useful, but the states themselves should remain predictable.

Alternative considered: introduce a model-scored support grade. Rejected for this slice because release validation needs deterministic behavior and understandable failures.

### Decision 5: Validate with curated benchmark questions

The benchmark layer should include pairs or variants of why questions that must map to the same primary accepted decision, plus cases that must stay limited or evidence-limited. This is more useful than only checking that any answer contains expected terms.

Alternative considered: add broad live-only validation. Rejected because live repository/provider output is useful for operators but too unstable as the default gate.

## Risks / Trade-offs

- Risk: Synonym rules become product-specific hacks -> Mitigation: keep them small, documented, and focused on recurring technical vocabulary already present in curated fixtures.
- Risk: Higher semantic weight increases false positives -> Mitigation: require source-ref or same-thread chunk support before upgrading answer state.
- Risk: Chunk support duplicates direct source refs -> Mitigation: de-duplicate normalized quotes and prefer direct source refs before chunk citations.
- Risk: Stronger support grading changes existing tests -> Mitigation: update tests around explicit states rather than broad answer prose.
- Risk: Benchmark expectations overfit one repository -> Mitigation: use bounded expected status, expected primary decision/thread, citations, and terms instead of exact generated answer text.

## Migration Plan

No database migration is expected. Existing artifact chunk metadata remains optional; missing metadata should reduce ranking bonus but not break retrieval.

Implementation can ship behind deterministic code paths:

- Add/adjust query normalization and retrieval ranking.
- Add same-thread chunk support selection where direct refs are insufficient.
- Update API answer context if needed.
- Update tests and benchmark fixtures.
- Run targeted engine/API, benchmark, web tests if copy changes, and OpenSpec validation.
