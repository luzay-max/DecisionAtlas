## 1. Refine imported candidate conversion in the engine

- [x] 1.1 Refine screened-in artifact family routing so rationale-heavy imported docs and strong PRs can choose a better-matched extraction path.
- [x] 1.2 Implement one bounded recovery extraction attempt for recoverable first-pass conversion failures on strong screened-in artifacts.
- [x] 1.3 Update conversion-loss recording and extraction summaries so final failure reasons remain diagnosable after the refined conversion path runs.

## 2. Align imported readiness and benchmark expectations

- [x] 2.1 Update imported-workspace readiness logic so `conversion_limited` is reported only after the refined conversion path is exhausted and `review_ready` wins once reviewable candidates exist.
- [x] 2.2 Extend lightweight real-repo benchmark fixtures to capture candidate-conversion expectations for the curated repositories used by this slice.
- [x] 2.3 Update benchmark validation code and any affected imported-workspace read-model tests to reflect the new candidate-conversion expectations.

## 3. Verify the real-repo conversion slice end to end

- [x] 3.1 Add or update extraction and import-job tests that cover recoverable first-pass failure, bounded recovery, and final conversion diagnostics.
- [x] 3.2 Add or update readiness and benchmark tests that prove a workspace can move out of `conversion_limited` when reviewable candidates are created.
- [x] 3.3 Run the engine test suite and benchmark validation, then record any curated real-repo follow-up validation needed before implementation is considered complete.

Validation follow-up: rerun the curated live real-repo import set after deployment, with special attention to `n8n-io/n8n`, to confirm the new `minimum_reviewable_candidates` expectation is met outside fixture-only validation.
