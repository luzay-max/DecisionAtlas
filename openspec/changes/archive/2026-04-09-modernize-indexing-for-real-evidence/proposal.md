## Why

DecisionAtlas now uses chunk-backed artifact evidence in imported why answers, so indexing quality has become a direct product concern instead of a hidden implementation detail. The current paragraph-and-fixed-slice chunking is too naive for rationale-heavy repository documents, which limits retrieval precision, evidence continuity, and later explanation quality.

## What Changes

- Introduce a structure-aware indexing capability for artifact chunks so markdown-style headings, section boundaries, and chunk overlap are preserved more intentionally.
- Add richer chunk metadata that later retrieval and evidence layers can use, such as heading path and chunk role.
- Update indexing behavior so the product can distinguish more clearly between structurally weak chunk evidence and stronger rationale-bearing chunk evidence.
- Update why retrieval expectations so chunk-backed supporting evidence benefits from the improved index structure without replacing accepted decisions as the answer anchor.

## Capabilities

### New Capabilities
- `indexing-real-evidence`: Structure-aware chunking and richer artifact-chunk metadata for retrieval and evidence quality.

### Modified Capabilities
- `why-search-retrieval-quality`: Supporting evidence retrieval should benefit from improved chunk structure and metadata while preserving accepted-decision-first answers.
- `real-repository-outcomes`: Imported workspaces should gain stronger evidence quality from improved indexing rather than only from prompt or review improvements.

## Impact

- Affected code in `services/engine/app/indexing/`, `services/engine/app/repositories/artifact_chunks.py`, and retrieval paths that consume artifact chunks.
- Likely migration impact if artifact chunk metadata schema changes.
- Validation impact on imported why answers and chunk-backed evidence behavior in real repositories.
