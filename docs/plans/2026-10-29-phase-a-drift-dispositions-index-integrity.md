# Phase A — F03 reviewed drift dispositions and F07 empty-index integrity

**Date:** 2026-10-29
**Base:** `main@8aa461f5bc30f16e023c9c00f0d641794fd16f86` (PR #27)
**Status:** Draft PR, not approved to merge.

## F03: Preserve review decisions on repeated detection
- In `DriftAlertRepository.create_or_update`, keep previously reviewed status, summary and disposition metadata rather than overwriting with an automated `open` signal. Manual reopen is recognized by existing handler fields.
- When recomputing semantic alert types, remove only **untouched open** alerts; retain handled alert IDs used by their audit events.
- Existing transient semantic downgrade and upgrade tests must still pass.

**Known boundary:** A reviewed historical alert is retained even if its source has changed. Correctly identifying a materially new observation requires a future revision-based fingerprint and is outside this PR. No migration or automatic reopening is introduced.

## F07: Reindexing an empty document clears old results
- On empty/whitespace-only chunker output, replace stored chunks with an empty list and commit.
- Preserve current nonempty embedder and transaction behavior.
- Use real ephemeral SQLite DB and fresh session reads to test nonempty → empty → whitespace → nonempty.

## Acceptance
- [ ] Existing semantic alert grouping and stale-type downgrade/upgrade regression tests pass.
- [ ] New false_positive semantic alert preserves disposition and ID across re-evaluation.
- [ ] New acknowledged rule-alert test preserves disposition and summary.
- [ ] Empty-content indexing removes stale chunks and subsequent nonempty reindex works.
- [ ] Full final-head GitHub Actions CI passes.
- [ ] Human review and runtime acceptance remain separate.

No private data, live tokens, real paid models, DB schema changes, or merge of Draft PRs #26/#28.
