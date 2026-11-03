# Stage B / B01 — bounded decision embedding cache and vector safety

**2026-11-03 · Draft implementation; no merge approval.** Base `main@2641989b443ca6633019fa7b713521be0ce5686d` after the Stage A default-disabled #28 merge and post-merge [CI #41573941870](https://github.com/luzay-max/DecisionAtlas/actions/runs/41573941870) SUCCESS. This is independent of #33/#34 runtime schema and private data retention P.

## Existing problem and intentionally narrow fix

`services/engine/app/retrieval/vector_search.py` formerly called `embedder.embed(decision_texts)` for every accepted decision on **every** Why query. It also used `zip` dot product without validating non-finite components, dimension equality or provider batch length; a mixed model could produce misleading rankings without an explicit error.

B01 now retains **only** validated decision vectors in a process-local, lock-protected LRU of **at most 256 entries**. Each key is scoped by owner/workspace/decision, the digest of all decision content fields, explicit stable embedding-provider namespace (provider URL + model + credential SHA256 fingerprint), and validated query dimensionality. Query embeddings are generated **every time**, not cached; only stable namespace opt-in is eligible. `FakeEmbedder` and arbitrary custom embedders without a declared stable namespace remain uncached: their synthetic output must not be presented as real vector retrieval.

- Repeated queries reuse unchanged accepted-decision vectors; content hash changes invalidate without a schema migration. Different provider namespace/model or dimension re-embeds rather than mixing vectors.
- Reject empty, enormous (dimension >8192), boolean/non-numeric, NaN, Inf, dimension-mismatched vectors and malformed embedding batches through existing `ProviderResponseError` (Why API handles it as 502). No silent `zip` truncation.
- Per-process lock and bounded entries reduce memory growth; double computation by concurrent cold requests is allowed and not claimed to be exactly-once.
- Redis/pgvector/HNSW/persistent embeddings, changes to source provenance, versioned `ArtifactRevision`, cross-worker invalidation, FakeEmbedder precision and paid LLM calls are **not** part of this PR.

## Verification and limits

Synthetic file-backed SQLite regression verifies first query vector work, second-query decision-vector cache hit (query always embedded), single decision edit invalidation, changed model identity/dimension re-embed, accepted-only scope, and failure on non-finite/mismatched vectors. Existing Why/hybrid regression and exact PR-head CI must pass.

**Operational limits:** process restart or another worker loses this bounded cache; an upstream endpoint that silently changes model weights under the exact same configured model name requires a documented config version change/restart. Provider-namespace digest is in-memory only; no raw API key or decision text is stored in cache keys. Decision vectors themselves may represent sensitive content, so do not persist them or expose them through logs. Use real authorized public-data tests later to measure p95, provider call count and ranking against a fixed sample; there are **no production accuracy/p95 claims** from Fake or synthetic tests.

**Next steps:** B02 Chinese bigram/English tech token lexical fallback and explicit retrieval mode as a separate PR; B03 remote same-origin API/Cookie contract; B04 Ubuntu+PostgreSQL integration. Track unrelated #41 N+1 evidence reads separately; no claim that B01 fixes it.

**Status:** DRAFT, not merged, needs new Head CI and maintainer review.
