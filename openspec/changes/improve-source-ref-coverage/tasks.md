## 1. Grounded Ref Retention

- [ ] 1.1 Inspect the current extraction/parser/source-ref path and identify where valid decisions stop after a single retained grounded quote.
- [ ] 1.2 Extend the grounding flow so one imported artifact can persist multiple grounded source refs for the same decision when multiple quotes are available.
- [ ] 1.3 Preserve exact-span safety checks so additional refs are skipped when they cannot be grounded confidently.

## 2. Coverage Diagnostics

- [ ] 2.1 Add machine-readable diagnostics for decisions that were created successfully but retained only thin grounded support.
- [ ] 2.2 Surface enough coverage data in summaries or validation outputs to distinguish thin source-ref coverage from broader extraction failure.

## 3. Validation

- [ ] 3.1 Add regression tests for valid extracted decisions that should retain more than one grounded source ref.
- [ ] 3.2 Add why-answer validation for imported cases that should move from `limited_support` toward `ok` once coverage improves.
- [ ] 3.3 Re-run imported why benchmark or live-style validation cases and record whether support-state distribution improves without increasing ungrounded refs.
