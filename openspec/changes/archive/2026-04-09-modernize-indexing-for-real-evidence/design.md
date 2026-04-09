## Context

DecisionAtlas originally treated artifact indexing as foundational infrastructure: split text into coarse chunks, embed each chunk, and store them for future use. That was acceptable while why-search relied mostly on accepted decisions, but it is now a direct product-quality issue because imported why answers already use chunk-backed supporting evidence.

Today the indexing path is still simple:

- `chunk_text()` splits on blank lines and hard slices long paragraphs
- chunks carry only `chunk_index`, `content`, and `embedding`
- retrieval has little structural context to distinguish heading-bearing rationale from generic body text

This creates three practical problems:

1. rationale text can be split at poor boundaries
2. cross-boundary meaning is lost because there is no overlap
3. chunk retrieval has too little metadata to favor richer supporting evidence later

## Goals / Non-Goals

**Goals:**

- make chunking structure-aware for markdown-style and document-style repository artifacts
- preserve limited overlap so evidence does not break at chunk boundaries
- enrich stored chunk metadata enough for later retrieval and explanation layers
- improve chunk-backed why evidence without changing accepted-decision-first answer anchoring

**Non-Goals:**

- redesign the full why-answering stack
- replace the embedding provider or require hosted-only embeddings
- build a full benchmark platform in this change
- introduce incremental chunk updates beyond the current replace-per-artifact model

## Decisions

### 1. Move from paragraph-only chunking to structure-aware chunking

The chunker will stop treating all content as flat paragraphs. It will prefer section-aware boundaries first:

- markdown headings
- blank-line paragraph groups
- bounded fallback slicing only when a section is still too large

Why this choice:

- it preserves rationale sections better than fixed slicing
- it does not require a heavyweight parser for the first iteration
- it fits the current repository-document mix, which is dominated by markdown, PR descriptions, and issue-like prose

Alternative considered:

- token-aware semantic chunking with an external parser. Rejected for now because it is a larger dependency and not necessary for the first modernization step.

### 2. Add small overlap instead of large rolling windows

Chunks will include bounded overlap only when large sections need subdivision.

Why this choice:

- it preserves cross-boundary meaning
- it keeps storage growth predictable
- it avoids a larger reranking rewrite in the same change

Alternative considered:

- no overlap. Rejected because it preserves the current boundary-loss problem.
- aggressive sliding windows. Rejected because it would inflate chunk count and retrieval noise too early.

### 3. Store richer metadata directly on artifact chunks

Artifact chunks need more than raw text. The change will extend stored chunk payloads with metadata such as:

- heading path
- section title
- chunk role or block type
- whether the chunk came from a structured section boundary or a fallback slice

Why this choice:

- why retrieval can prefer chunks that come from rationale-bearing sections
- later explanation layers can describe where evidence came from
- the current replace-per-artifact indexing model makes schema extension straightforward

Alternative considered:

- infer all structure at retrieval time from raw content. Rejected because it repeats work and keeps retrieval blind during ranking.

### 4. Keep accepted decisions as the why-answer anchor

Improved chunk structure will only strengthen supporting evidence. It will not change the rule that accepted decisions remain the trust anchor for why answers.

Why this choice:

- the recent why improvements were built around accepted-decision grounding
- using raw chunk evidence as the primary answer source would blur the review boundary again

Alternative considered:

- direct chunk-first why answers. Rejected because it weakens the review-and-accept model.

## Risks / Trade-offs

- [More chunk rows and storage growth] -> Keep overlap bounded and avoid aggressive sliding windows in the first version.
- [Schema migration risk for `artifact_chunks`] -> Use additive metadata fields and preserve compatibility with older rows during rollout.
- [Retrieval noise from too much metadata] -> Keep the first metadata set small and focused on heading/section semantics.
- [Uneven benefit across artifact types] -> Accept that markdown-heavy docs improve most first; PRs and issues can still use the fallback path.

## Migration Plan

1. Add additive metadata fields for artifact chunks.
2. Update indexing to write the richer chunk payload.
3. Keep retrieval tolerant of missing metadata while older rows still exist.
4. Reindex artifacts in local and imported workspaces so chunk-backed why answers can benefit from the new structure.

## Open Questions

- Whether section metadata should live in explicit columns or a single JSON metadata field.
- Whether the first iteration should expose chunk metadata in diagnostics or keep it internal to retrieval.
