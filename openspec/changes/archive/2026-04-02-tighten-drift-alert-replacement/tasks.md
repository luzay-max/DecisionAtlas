## 1. Drift Alert Replacement

- [x] 1.1 Update reevaluation persistence so stale semantic drift alerts are cleared before the latest reevaluation results are stored.
- [x] 1.2 Ensure cross-type replacement works for the same artifact-decision thread, including `possible_supersession` to `needs_review` and the reverse.
- [x] 1.3 Keep grouped weak follow-up regeneration intact after stale semantic alerts are removed.

## 2. API And UI Consistency

- [x] 2.1 Verify the drift API only returns the latest semantic conclusions after reevaluation.
- [x] 2.2 Verify the imported drift UI no longer shows contradictory old and new alert cards for the same thread.
- [x] 2.3 Keep manual reevaluation flow unchanged while updating only stale-alert replacement behavior.

## 3. Validation

- [x] 3.1 Add engine regression coverage for downgraded and upgraded artifact-decision threads so stale alert rows are not retained.
- [x] 3.2 Add API or web regression coverage for the browser-use style case where old `possible_supersession` alerts previously remained visible after reevaluation.
- [x] 3.3 Re-run `openspec status --change "tighten-drift-alert-replacement" --json` and confirm the change is apply-ready with all artifacts present.
