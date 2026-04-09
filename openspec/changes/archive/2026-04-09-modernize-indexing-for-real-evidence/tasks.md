## 1. Structure-aware chunking

- [x] 1.1 Replace flat paragraph-only chunking with structure-aware chunking that prefers section boundaries and only falls back to bounded slicing when necessary.
- [x] 1.2 Add bounded overlap for split sections so cross-boundary rationale can still be recovered.

## 2. Chunk metadata and storage

- [x] 2.1 Extend artifact chunk storage to retain structural metadata such as heading path, section label, or chunk role.
- [x] 2.2 Keep indexing and retrieval compatible while workspaces may contain a mix of older and newer chunk rows.

## 3. Retrieval integration and validation

- [x] 3.1 Update why supporting-evidence retrieval to benefit from chunk structure and metadata without changing accepted-decision-first anchoring.
- [x] 3.2 Add regression coverage for structure-aware chunking, chunk metadata persistence, and structured supporting-evidence ranking.
- [x] 3.3 Validate at least one imported real-repo why case where structured chunk evidence improves support quality or evidence ranking.
