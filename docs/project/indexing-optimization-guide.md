# Indexing Optimization Guide

This is a living document for improving DecisionAtlas indexing over time.

Use it for three purposes:

1. Record how indexing works today.
2. Capture concrete optimization ideas without losing context.
3. Keep a prioritized backlog for future implementation work.

Whenever a new indexing issue, bottleneck, or improvement idea appears, add it here instead of keeping it only in chat or ad hoc notes.

## Scope

This guide covers the artifact indexing path in the engine:

```text
artifact.content
  -> chunk_text()
  -> embedder.embed(chunks)
  -> artifact_chunks table
```

Relevant files:

- [chunker.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/indexing/chunker.py)
- [index_artifact.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/indexing/index_artifact.py)
- [embedder.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/indexing/embedder.py)
- [artifact_chunks.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/repositories/artifact_chunks.py)
- [hybrid.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/hybrid.py)
- [vector_search.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/vector_search.py)
- [full_text.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/full_text.py)

## Current Implementation

### 1. Chunking

Current behavior:

- Trim the artifact content.
- Split by blank lines.
- Keep each paragraph as one chunk if it is `<= 400` characters.
- If a paragraph is longer than `400` characters, split it into fixed 400-character slices.

Implications:

- Simple and fast.
- No token awareness.
- No overlap between chunks.
- No markdown-heading awareness.
- No section-level structure preservation.

### 2. Embedding

Current behavior:

- `FakeEmbedder` returns a tiny synthetic vector based on text length and index.
- `OpenAICompatibleEmbedder` calls `/embeddings` on a provider-compatible endpoint.

Current local runtime:

- `.env` currently uses `EMBEDDING_PROVIDER_MODE=fake`
- This means indexing is often structurally present but semantically weak in local runs.

Implications:

- Index rows are created successfully.
- Semantic retrieval quality is not representative when fake embeddings are active.

### 3. Storage

Current behavior:

- Every artifact is indexed into `artifact_chunks`.
- Re-indexing uses a full replace strategy per artifact:
  - delete old chunks
  - insert new chunks

Implications:

- Easy to reason about.
- Idempotent at the artifact level.
- Not incremental.

### 4. Retrieval Reality

Important current limitation:

- The project already builds chunk-level artifact indexes.
- But the main why-search path still retrieves mostly from structured decisions, not directly from `artifact_chunks`.

Current retrieval stack:

- full-text search over accepted decisions
- vector search over accepted decision text
- hybrid merge of those two

Implications:

- Improving indexing alone may not immediately improve user-facing why-search.
- The current bottleneck for imported-workspace quality is often upstream:
  - signal selection
  - extraction quality
  - accepted decision quality

## Main Weaknesses Today

### Weakness 1: Chunking is too naive

Symptoms:

- Semantic boundaries are broken by fixed character slicing.
- Lists, sections, and heading hierarchies are flattened.
- Long rationale paragraphs may be split at poor boundaries.

Why it matters:

- Lower retrieval precision.
- Harder to preserve meaningful evidence spans.

### Weakness 2: No overlap

Symptoms:

- Cross-boundary meaning is lost when a key phrase starts at the end of one chunk and finishes in the next.

Why it matters:

- Retrieval misses concepts spread across adjacent text.

### Weakness 3: Index quality depends heavily on fake embeddings in local runs

Symptoms:

- Artifact chunk embeddings exist, but do not reflect true semantics.

Why it matters:

- Optimization experiments on chunking are hard to evaluate honestly when embeddings are fake.

### Weakness 4: Chunk metadata is too thin

Symptoms:

- Chunks currently store content and embedding, but not richer structural context such as:
  - section title
  - heading path
  - markdown block type
  - normalized document role

Why it matters:

- Later retrieval, reranking, and explanation layers have less context to work with.

### Weakness 5: Main product retrieval does not fully consume the chunk index

Symptoms:

- Why-search mainly operates over accepted decisions.
- Artifact chunk indexing is more foundational than product-critical right now.

Why it matters:

- Some indexing improvements may have delayed rather than immediate product impact.

## Decision Extraction Performance

Although this document is centered on indexing, indexing quality and extraction latency are tightly connected in the current product.

The current imported-workspace flow is:

```text
import artifacts
  -> index artifacts
  -> extract candidate decisions
  -> review
  -> accepted decisions
  -> why / timeline / drift
```

In practice, imported-repo performance pain is often felt most strongly in the extraction phase, not the indexing phase.

### Current Extraction Design

Relevant files:

- [pipeline.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/extractor/pipeline.py)
- [openai_compatible.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/llm/openai_compatible.py)
- [github_document_selection.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/ingest/github_document_selection.py)
- [decision-extraction.md](C:/Users/Max/Desktop/DecisionAtlas/packages/prompts/decision-extraction.md)

Current behavior:

- High-signal artifacts are ranked with simple heuristics.
- The extraction pipeline processes artifacts sequentially.
- Each selected artifact triggers one remote `/chat/completions` request.
- Each request may include up to `12000` characters of artifact content.
- The model is asked to produce a full structured JSON candidate decision.
- Local live runs currently use `.env` with `LLM_MODEL=deepseek-chat` and `LLM_TIMEOUT_SECONDS=60`.

### Why Extraction Feels Slow

There are four main causes.

#### Cause 1: Serial execution

The pipeline sends one extraction request at a time.

Implication:

- Total extraction time grows roughly linearly with the number of candidate artifacts.
- Even acceptable per-request latency becomes slow at repository scale.

#### Cause 2: Heavy per-request payloads

The extraction request may include up to `12000` characters of source text.

Implication:

- Every request is a relatively heavy long-context structured extraction call.
- Slow responses and provider timeouts become much more likely.

#### Cause 3: The shortlist is still broader than ideal

Document and artifact filtering is better than before, but still sends a non-trivial number of artifacts into the LLM stage.

Implication:

- The system may spend time extracting from artifacts that are “possibly relevant” instead of “highly likely to contain a concrete engineering decision.”

#### Cause 4: Full extraction is used as the first LLM step

The current pipeline does not separate:

- “is this likely to contain a real decision?”
- from
- “extract a full structured candidate decision JSON.”

Implication:

- Expensive structured extraction is being used too early and too often.

### Recommended Extraction Optimization Order

#### Priority 1: Shrink the extraction shortlist

Recommendation:

- Send fewer artifacts into the LLM extraction stage.
- Be more aggressive about preferring rationale-heavy docs and high-signal PRs.

Examples of better first-class candidates:

- ADRs
- RFCs
- architecture docs
- migration docs
- rollout plans
- release notes with rationale
- PR descriptions that clearly explain tradeoffs

Examples of lower-priority candidates:

- generic issues
- short commits
- broad README sections
- operational text without a clear decision

Why this is first:

- The easiest way to improve total latency is to reduce the number of LLM calls.

#### Priority 2: Reduce extraction input size

Recommendation:

- Lower extraction input size from the current `12000`-character ceiling.
- Prefer extracting only the most relevant sections or paragraphs instead of raw head/tail truncation.

Why:

- Many long docs contain only one small section with actual rationale.
- Sending the entire large context is often wasteful.

Expected benefit:

- Faster requests.
- Fewer provider timeouts.

#### Priority 3: Split extraction into two stages

Recommendation:

- Stage A: fast yes/no decision-likeness screening.
- Stage B: full structured JSON extraction only for artifacts that pass Stage A.

Why:

- Many artifacts are not truly decision-bearing.
- A cheap screening pass can dramatically reduce the expensive extraction volume.

Expected benefit:

- Better throughput.
- Lower model cost.

#### Priority 4: Add limited concurrency

Recommendation:

- Move from fully serial extraction to a small bounded concurrency model, such as `2-4` in-flight requests.

Why:

- Sequential extraction leaves a lot of wall-clock time on the table.

Important caution:

- Do not jump straight to high concurrency.
- Start with a low cap to avoid rate-limit storms and harder debugging.

#### Priority 5: Consider model specialization only after the pipeline is thinner

Recommendation:

- Evaluate alternative models only after shortlist size and request size are under control.

Why:

- A stronger or slower reasoning model may improve quality, but it does not solve the basic throughput problem by itself.
- Model changes are easier to evaluate once the pipeline shape is healthier.

### What Not To Optimize First

These are lower leverage for the current problem.

1. Do not start with multimodal models.
   Reason:
   The extraction pipeline is currently text-only.

2. Do not start by only increasing timeout values.
   Reason:
   That delays failure but does not improve throughput.

3. Do not expect indexing-only changes to fix extraction latency.
   Reason:
   Indexing and extraction are adjacent, but the current slowness is mostly driven by LLM extraction behavior.

### Extraction Performance Backlog

Use this as a dedicated backlog for the “decision extraction is slow” problem.

1. Tighten artifact signal scoring to reduce low-value LLM calls.
2. Lower `MAX_EXTRACTION_ARTIFACT_CHARS` after benchmark comparison.
3. Add paragraph-level relevance selection before full extraction.
4. Add a cheap screening prompt before full JSON extraction.
5. Add bounded concurrency for extraction requests.
6. Record extraction duration statistics per import job.
7. Store counts for:
   - shortlisted artifacts
   - extracted artifacts
   - skipped low-signal artifacts
   - skipped timeout artifacts
8. Compare `deepseek-chat` vs a stronger reasoning model only after the above changes.

### Suggested Metrics For Future Tracking

For each imported workspace run, track:

- number of artifacts imported
- number of artifacts shortlisted for extraction
- number of extraction requests sent
- average extraction request duration
- p95 extraction request duration
- timeout count
- candidate decisions created
- candidate decisions accepted later

These metrics will make future extraction optimization decisions much easier.

## Why-Search Optimization

Why-search is closely related to indexing and extraction quality, because the answer pipeline depends on accepted decisions and their supporting evidence.

Relevant files:

- [answering.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/answering.py)
- [query.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/api/query.py)
- [query_rewrite.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/query_rewrite.py)
- [hybrid.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/hybrid.py)
- [full_text.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/full_text.py)
- [vector_search.py](C:/Users/Max/Desktop/DecisionAtlas/services/engine/app/retrieval/vector_search.py)

### Current Why-Search Design

Current flow:

```text
question
  -> rewrite_query()
  -> hybrid_search() over accepted decisions
  -> top decision hits
  -> source refs
  -> stitched answer + citations
```

Important current behavior:

- Imported workspaces are blocked from trustworthy why-search unless they already have accepted decisions.
- Query rewrite is currently only whitespace normalization and lowercasing.
- Full-text retrieval is the dominant signal.
- Vector retrieval is only a weak supplement.
- The final answer is assembled from structured decision fields, not generated by a separate answer model.

### Current Strengths

1. Conservative trust boundary.
   The system does not freely answer imported why-questions without accepted decision grounding.

2. Explainable output.
   Answers map back to decisions and source refs.

3. Operational simplicity.
   The system avoids a second answer-generation LLM call in the main path.

### Current Weaknesses

#### Weakness 1: Retrieval target is too narrow

Current behavior:

- Why-search primarily retrieves accepted decisions.
- It does not directly use artifact chunk retrieval as a main evidence layer.

Implication:

- Imported workspaces can feel empty even after useful docs are imported.
- The answer pipeline is bottlenecked by accepted-decision coverage.

#### Weakness 2: Query rewrite is extremely weak

Current behavior:

- `rewrite_query()` only normalizes whitespace and lowercase.

Implication:

- Slight wording mismatches between user questions and decision text reduce recall.

#### Weakness 3: Vector retrieval weight is very low

Current behavior:

- In hybrid search, vector scores are scaled down aggressively.

Implication:

- Why-search behaves mostly like keyword search.
- Semantic recall is underused.

#### Weakness 4: Answer assembly is mechanical

Current behavior:

- The system concatenates:
  - decision title
  - chosen option
  - tradeoffs

Implication:

- Answers may feel like stitched summaries rather than targeted explanations.

#### Weakness 5: Citation sufficiency is rigid

Current behavior:

- Fewer than two citations often collapses into insufficient evidence.

Implication:

- Some potentially useful answers are discarded even when one strong source ref exists.

### Recommended Why-Search Optimization Order

#### Priority 1: Improve query rewrite

Recommendation:

- Expand query normalization beyond lowercase and whitespace cleanup.
- Add technical synonym handling and alias normalization.

Examples:

- queue <-> background jobs
- source of truth <-> primary database
- cache-only <-> cache only
- rollout <-> migration

Why this is first:

- It is cheap compared to larger retrieval refactors.
- It improves both full-text and vector retrieval quality.

#### Priority 2: Rebalance hybrid retrieval weights

Recommendation:

- Benchmark vector contribution instead of keeping it near-negligible.

Why:

- The current hybrid path leans too hard on exact wording matches.

Expected benefit:

- Better recall for semantically related questions.

#### Priority 3: Add artifact-chunk evidence retrieval as a support layer

Recommendation:

- Keep accepted decisions as the primary trust anchor.
- Add artifact chunk retrieval to improve grounding and evidence richness.

Possible uses:

- support retrieved decisions with more precise evidence snippets
- add a clearly labeled raw-evidence fallback when accepted coverage is sparse

Why:

- This better uses the index the system is already building.

#### Priority 4: Improve answer composition without turning it into unconstrained generation

Recommendation:

- Keep answers grounded in accepted decisions and source refs.
- Replace direct field concatenation with a more structured explanation template.

Example goals:

- answer the actual question more directly
- explain rationale, not just decision metadata
- preserve citations and trust boundaries

#### Priority 5: Add more nuanced evidence states

Recommendation:

- Replace the current binary threshold with graded outcomes such as:
  - `ok`
  - `limited_support`
  - `review_required`
  - `insufficient_evidence`

Why:

- This better reflects partial but still useful evidence.

### What Not To Optimize First

1. Do not start by replacing the whole why path with a free-form answer LLM.
   Reason:
   Trust and citation quality would likely regress before retrieval quality improves.

2. Do not treat indexing improvements as sufficient by themselves.
   Reason:
   Why-search still needs better query handling and better retrieval composition.

3. Do not optimize the final answer wording before improving recall.
   Reason:
   Better phrasing does not fix wrong or missing retrieval.

### Why-Search Backlog

1. Add technical synonym normalization in `rewrite_query()`.
2. Add repo-specific alias dictionaries where useful.
3. Benchmark different vector score weights in hybrid retrieval.
4. Add chunk-level supporting evidence retrieval for accepted decisions.
5. Add imported-workspace fallback evidence exploration when accepted coverage is sparse.
6. Improve answer templates to use `problem + chosen_option + tradeoffs + source_quote`.
7. Introduce graded evidence states instead of hard binary sufficiency only.
8. Add benchmark questions for imported repos and compare retrieval hit quality over time.

### Suggested Why-Search Metrics

Track these over time:

- question count
- accepted-decision hit rate
- citation count per answer
- insufficient-evidence rate
- review-required rate for imported workspaces
- average time-to-first-useful-answer after import
- answer usefulness on benchmark repo questions

### Current Recommendation

If only one why-search improvement is pursued next, the best first move is:

**improve query rewrite and rebalance hybrid retrieval before changing answer generation**

That order is recommended because:

- current retrieval recall is the main bottleneck
- accepted decisions are still the trust boundary
- better recall improves the whole path without weakening explainability

## Recommended Optimization Order

### Priority 1: Make embedding quality real before over-optimizing chunking

Recommendation:

- Turn on a real embedding provider for benchmarking and optimization work.

Why:

- If embeddings stay fake, chunking improvements are difficult to measure accurately.

Expected benefit:

- Better signal about whether chunk changes are actually helping retrieval.

### Priority 2: Replace fixed char chunking with structure-aware chunking

Recommendation:

- Chunk markdown by headings first.
- Then chunk by paragraph groups.
- Only fall back to fixed-size splits when sections are still too large.

Why:

- Repository docs are often structured.
- Preserving that structure improves semantic coherence.

Expected benefit:

- Better retrieval quality.
- Better evidence snippets.

### Priority 3: Add overlap

Recommendation:

- Add a small overlap window between oversized chunks.

Why:

- Reduces boundary loss for adjacent concepts.

Expected benefit:

- Fewer misses on long rationale-heavy documents.

### Priority 4: Add chunk metadata

Recommendation:

- Store extra metadata for each chunk, for example:
  - artifact path
  - heading text
  - section order
  - source document category

Why:

- Enables better reranking and downstream explanations.

Expected benefit:

- Better debugging and better future retrieval quality.

### Priority 5: Introduce artifact-chunk retrieval into real user flows

Recommendation:

- Use chunk retrieval as a supporting evidence layer for imported why-search and future evidence exploration.

Why:

- Without this step, the chunk index remains mostly infrastructure.

Expected benefit:

- Better grounding for imported workspaces.
- More useful behavior when accepted decisions are sparse.

## Optimization Ideas Backlog

Use this section as a backlog. Keep each item small and concrete.

### Candidate Ideas

1. Add markdown-heading-aware chunking.
2. Add chunk overlap for oversized sections.
3. Store chunk metadata like heading and path.
4. Add a benchmark comparing fake embeddings vs real embeddings on the same repo set.
5. Add chunk retrieval for evidence inspection in imported workspaces.
6. Measure indexing time and chunk counts per imported workspace.
7. Add document-type-specific chunking rules for ADRs, RFCs, changelogs, and runbooks.

## Evaluation Framework

Before shipping an indexing change, evaluate it with the same questions:

### Quality

- Do imported repos produce more relevant evidence?
- Do retrieved snippets preserve better semantic boundaries?
- Does why-search become more trustworthy when chunk retrieval is used?

### Cost

- Does indexing get materially slower?
- Do embedding calls increase too much?
- Does storage growth remain reasonable?

### Robustness

- Does the index still build successfully on large repos?
- Does the chunker avoid provider failures caused by oversized inputs?
- Does re-indexing remain idempotent?

### Product Impact

- Does the change improve current user-visible behavior now?
- Or is it mostly preparing the foundation for a later retrieval upgrade?

## Suggested Future Experiments

### Experiment A: Structure-aware chunking

Goal:

- Compare current blank-line chunking vs markdown-heading chunking.

Success signal:

- Better evidence coherence on imported repos with ADRs and architecture docs.

### Experiment B: Real embedding benchmark

Goal:

- Compare retrieval results using fake embeddings vs a real embedding model.

Success signal:

- Clear evidence that chunk-level retrieval becomes meaningfully more semantic.

### Experiment C: Chunk-backed imported why-search fallback

Goal:

- When accepted decisions are sparse, fall back to clearly labeled evidence exploration over artifact chunks.

Success signal:

- Imported workspaces feel less empty after successful import.

## Rules For Updating This Document

When adding a new optimization item, include:

1. The problem being observed.
2. Where it appears in code or product behavior.
3. Why it matters.
4. The proposed change.
5. How success should be measured.

Preferred entry format:

```md
### Optimization: <short title>

Problem:
- ...

Current behavior:
- ...

Proposed change:
- ...

Expected benefit:
- ...

Risks:
- ...

Validation:
- ...
```

## Current Recommendation

If only one indexing improvement is pursued next, the best first move is:

**enable real embedding evaluation and then implement structure-aware chunking**

That order is recommended because:

- It gives truthful retrieval feedback.
- It preserves repository-document structure better.
- It is more likely to produce meaningful long-term gains than tuning fixed character limits alone.
