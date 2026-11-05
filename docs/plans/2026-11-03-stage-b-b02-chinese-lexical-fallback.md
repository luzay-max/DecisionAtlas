# Stage B / B02 — Chinese and mixed-language retrieval, honest lexical fallback

**2026-11-03 · Draft implementation.** Base: `main@2641989b443ca6633019fa7b713521be0ce5686d` (Stage A approved and [post-merge CI #41573941870](https://github.com/luzay-max/DecisionAtlas/actions/runs/41573941870) SUCCESS). B01 [Draft #43](https://github.com/luzay-max/DecisionAtlas/pull/43) remains separate and **unmerged**; this B02 branch does not incorporate B01 code.

## Reproduced baseline deficiencies

- `query_rewrite.expand_query_terms` and `full_text._tokenize` used an English-only regular expression. Pure Chinese questions were silently converted to zero terms and could not retrieve Chinese accepted decisions lexically.
- `hybrid_search` invariably called `vector_search`, including with `FakeEmbedder`; this synthetic dimensional/length embedding was treated like semantic relevance and could rank unrelated accepted decisions.
- Real embedding endpoint exceptions returned errors with no usable lexical fallback; Why responses did not disclose whether semantic retrieval actually ran.

## B02 changes

1. Reuse the existing query rewrite/English alias contract. Preserve NFKC Chinese text, split contiguous Han runs into overlapping two-character grams (single Han character stays one token) and keep Latin technical identifiers such as PostgreSQL, Redis, RabbitMQ, XXL-JOB. Remove common Chinese question-only expressions from the query. Normalize candidate text with NFKC/casefold and preserve title/decision/problem/tradeoffs/context/constraints weights.
2. `hybrid_search_with_mode` explicitly returns one of `hybrid`, `lexical_only` (FakeEmbedder) and `lexical_fallback` (provider error). Retain old list-returning `hybrid_search` for existing callers. No synthetic vector hits in the lexical modes. Both lexical paths operate solely on previously accepted decisions and the authorized workspace.
3. Why response includes `retrieval_mode` at top level and in `answer_context`; `not_run` when no accepted baseline is available. Optional chunk supporting citations also avoid FakeEmbedder vectors, and a provider outage cannot defeat an already-grounded lexical response.

## Test and limits

Synthetic file-backed SQLite regressions cover pure Chinese, Chinese+PostgreSQL, RabbitMQ+XXL-JOB, unrelated Chinese, workspace and candidate isolation, fake-no-embed, embedding timeout fallback and API-level Why disclosure. Existing English lexical, hybrid and Why regression suites remain authoritative.

**Not claimed:** language model intent understanding, Chinese morphological segmentation, semantic synonym recall, actual Chinese recall@k/precision@k, real provider economics or end-to-end source-version provenance. Bigram substring retrieval can have false positives and needs separately recorded public evaluation; an actual returned quote must still pass Why evidence gates. For fallback, do not silently claim semantic success. B01 vector caching remains in Draft #43; CI validation here is against the existing main vector path. No PostgreSQL schema change, paid provider, private GitHub import or #28 enablement.

**Merge gate:** new exact-head CI, review of older English/Why regressions, deterministic negative controls, independent maintainer authorization. **Draft/unmerged.**
