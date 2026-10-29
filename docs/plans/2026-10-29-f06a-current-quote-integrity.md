# F06a — Detect current-source quote mismatches without changing review history

**Date:** 2026-10-29  
**Base:** `main@8aa461f5bc30f16e023c9c00f0d641794fd16f86` (PR #27)  
**Status:** Draft PR; independent of Draft PRs #26/#28/#29/#30/#31.

## Problem
Artifacts are upserted in place, while SourceRefs are keyed to a mutable Artifact ID. A source can change after extraction and review; existing SourceRef quotes then no longer appear in the current content. Previously the decision API did not expose this mismatch.

## F06a — Minimal read-only detection
- In decision list/detail, add `review_evidence.current_quote_integrity` with status `no_refs`, `current_quotes_found`, `current_quote_missing`, or `unverifiable` and separate found/missing/unknown counts.
- In the source refs' list/detail payloads, add nullable `current_quote_match`: true for exact current-content substring, false for absent exact quote, null for missing artifact/empty quote.
- Keep candidate quality scores, review state, old quotes, original SourceRef IDs and decision audit history unchanged. This is a read-only diagnostic, not a model accuracy statement or source attestation.
- Tests demonstrate an Artifact content overwrite produces a visible mismatch in both list/detail without changing the reviewed decision or historical SourceRef quote. Additional test ensures unknown is not reported as mismatch.

## Explicit limits
This does **not** preserve the historical artifact content or SHA snapshot and does **not** fix re-extraction of changed artifacts. Exact quote matching can be sensitive to formatting-only edits; a positive match does not prove authenticity, version identity, or approval. A complete F06 requires versioned ArtifactRevision, SourceRef->revision binding, a review-safe re-extraction policy and migration/backfill design, handled in separate gated PRs.

## CI acceptance
- [ ] Existing Engine/API contract tests pass.
- [ ] New SQLite API tests show quote present → missing after mutable overwrite, old refs unchanged, and unknown semantics.
- [ ] Full GitHub Actions CI passes on final SHA.
- [ ] Human review and operator-controlled integration acceptance remain separate.

No database migration, new GitHub calls, private data, real tokens, paid model calls or automatic merge.
