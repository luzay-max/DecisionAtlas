## 1. Report Contract And Entry Point

- [x] 1.1 Define the governance drift report schema with `status`, `signals`, `human_decisions_needed`, `recommended_next_actions`, and `context`.
- [x] 1.2 Add a local governance drift detection entrypoint separate from the existing diff checker.
- [x] 1.3 Ensure the entrypoint returns machine-readable JSON suitable for future AI agent calls.

## 2. Context Collection

- [x] 2.1 Collect bounded roadmap and plan document references from `docs/plans`.
- [x] 2.2 Collect main OpenSpec specs and their requirement names as governance baseline context.
- [x] 2.3 Collect archived OpenSpec proposal, design, task, and spec delta summaries from recent archived changes.
- [x] 2.4 Collect update logs and postmortem-style documents from project documentation.
- [x] 2.5 Collect accepted governance rules from provided input or the configured local database when available.
- [x] 2.6 Optionally collect current git diff paths and excerpts as recent evidence.

## 3. Drift Signal Evaluation

- [x] 3.1 Detect `roadmap_mismatch` signals when recent governance history appears outside the current roadmap direction.
- [x] 3.2 Detect `spec_gap` signals when archived or recent behavior changes are not reflected in main specs.
- [x] 3.3 Detect `stale_rule` signals when deprecated, superseded, rejected, or draft governance sources appear to be reused as active guidance.
- [x] 3.4 Detect `repeated_postmortem_issue` signals by comparing historical issue descriptions with recent evidence.
- [x] 3.5 Detect `unsynced_decision` signals when human decisions appear in proposals, designs, tasks, logs, or roadmap text without matching specs or accepted rules.
- [x] 3.6 Compute conservative overall status: `clean`, `watch`, `drift_detected`, or `review_required`.

## 4. Documentation And Tests

- [x] 4.1 Add deterministic fixtures for clean, watch, drift-detected, and review-required governance drift reports.
- [x] 4.2 Add tests for context collection, each signal type, status computation, and advisory-only behavior.
- [x] 4.3 Document how to run the drift detector and interpret report statuses and signal types.
- [x] 4.4 Run targeted governance drift tests.
- [x] 4.5 Run OpenSpec strict validation for the change.
- [x] 4.6 Run the practical project validation gate or document any environment-limited skip.
