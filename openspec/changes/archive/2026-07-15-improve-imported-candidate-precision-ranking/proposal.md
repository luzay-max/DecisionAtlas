## Why

Real imported repositories can produce a long review queue where confidence-only ordering puts salvaged, thin, or semantically repeated candidates ahead of better-grounded decisions. The next product-quality step is to make the queue deterministic and evidence-first so reviewers spend their first minutes on the candidates most likely to establish a useful baseline.

## What Changes

- Persist bounded per-candidate extraction provenance, including artifact family, parser salvage, and recovery path, without storing raw provider output.
- Compute a deterministic candidate precision profile from grounding, confidence, artifact family, extraction provenance, and decision specificity.
- Detect near-duplicate candidate clusters within a workspace and designate one strongest representative without deleting audit evidence.
- Rank imported candidate queues by precision tier and score, with stable tie-breaking.
- Expose strong, partial, and weak tiers plus duplicate and extraction-origin explanations in API and review UI.
- Keep every candidate individually reviewable; batch review and precision trend reporting remain follow-up changes.

## Capabilities

### New Capabilities
- `candidate-precision-ranking`: Deterministic evidence-first candidate profiling, near-duplicate clustering, and stable review-queue ordering.

### Modified Capabilities
- `decision-extraction-conversion`: Persist bounded extraction provenance on each newly created candidate.
- `imported-review-decision-quality`: Show ranking tier, extraction origin, and duplicate-cluster context in imported review cards.

## Impact

- Adds one backward-compatible engine database migration and optional candidate metadata for existing rows.
- Changes `GET /decisions?review_state=candidate` ordering and response fields while preserving existing fields and review actions.
- Affects extraction persistence, decision serialization, review components, API types, tests, benchmark evidence, and dated project documentation.
- Does not auto-reject, auto-accept, or delete candidates and does not expose raw model responses.
