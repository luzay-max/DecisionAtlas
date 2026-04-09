## Context

The current imported why path is already conservative: it answers through accepted decisions, keeps a primary decision focus, and exposes `limited_support` instead of bluffing. The remaining weakness is retrieval quality. Query rewrite is still shallow, hybrid search leans too hard on exact wording, and artifact chunks are indexed but barely used in the user-facing why flow.

The next step is to improve recall and evidence richness without weakening the accepted-decision trust boundary. This is cross-cutting because it touches query normalization, retrieval ranking, evidence assembly, and imported-workspace answer behavior.

## Goals / Non-Goals

**Goals:**
- Improve accepted-decision recall for technically equivalent why-questions.
- Make vector similarity materially useful in hybrid retrieval.
- Use artifact chunks as a support layer to strengthen grounded evidence for accepted decisions.
- Preserve the current trust model: accepted decisions remain the answer anchor.
- Create a benchmarkable path for imported why quality improvements.

**Non-Goals:**
- Replacing the why path with unconstrained generation.
- Removing `limited_support`, `review_required`, or other existing evidence states.
- Reworking extraction, acceptance review, or drift semantics as part of this change.
- Turning chunk retrieval into a fully separate raw-evidence answer mode.

## Decisions

### 1. Strengthen query rewrite before deeper retrieval refactors
`rewrite_query()` will expand beyond lowercase and whitespace normalization. It should normalize a small technical alias layer, collapse equivalent punctuation or hyphenation variants, and preserve question intent instead of broadening to topic-level search.

Why:
- This is the cheapest recall win.
- It improves both full-text and vector paths.

Alternative considered:
- Rely only on vector search improvements.
Why not:
- Exact wording still dominates many imported repo questions, and weak normalization keeps pushing retrieval toward neighboring decisions.

### 2. Rebalance hybrid retrieval rather than replacing it
Hybrid search should keep both full-text and vector components, but vector influence will be raised from a weak supplement to a real scoring contributor. Exact weighting should be benchmarked with imported why questions instead of hard-coded by intuition.

Why:
- Full-text remains useful for explicit repo terminology.
- Vector search helps recover semantically similar phrasings that full-text misses.

Alternative considered:
- Switch to vector-first retrieval.
Why not:
- That would risk dropping precise repository wording and make debugging harder.

### 3. Keep accepted decisions as the trust anchor and add chunk evidence behind them
Artifact chunks will be retrieved only after a candidate accepted decision is selected. Chunk retrieval will help support, explain, and strengthen evidence for the accepted decision rather than compete with it as an independent answer source.

Why:
- This uses the existing chunk index without weakening the answer contract.
- It can improve citation density and answer specificity.

Alternative considered:
- Query chunks directly and answer from chunks when accepted decisions are sparse.
Why not:
- That blurs the trust boundary and would need a separate product contract.

### 4. Improve answer composition only as far as retrieval-backed explanation quality
Answer assembly can become more direct and question-aware, but only using accepted decision fields plus retrieved supporting chunks/source refs. This stays a structured composition change, not a second answer-generation model stage.

Why:
- Better retrieval should produce better evidence, and the answer should expose that value.
- A mechanical field concatenation path underuses improved retrieval.

Alternative considered:
- Keep the exact current answer formatter.
Why not:
- Retrieval improvements would be less visible to the user if the answer body stays overly mechanical.

## Risks / Trade-offs

- [Risk] Better rewrite rules may over-normalize distinct technical concepts. -> Mitigation: keep alias rules small, explicit, and benchmarked against real repo questions.
- [Risk] Raising vector weight may introduce semantically related but wrong neighboring decisions. -> Mitigation: benchmark hybrid weights and keep accepted-decision scoring inspectable.
- [Risk] Chunk evidence support may surface noisy artifact snippets. -> Mitigation: use chunk retrieval only after accepted-decision selection and filter support chunks by decision relevance.
- [Risk] More retrieval logic increases test surface. -> Mitigation: add imported why regression cases and keep the contract centered on current evidence states.
