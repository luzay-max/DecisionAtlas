## 1. Sparse Recovery Selection

- [x] 1.1 Extract deterministic sparse-recovery eligibility and family-diverse artifact selection helpers from the import pipeline.
- [x] 1.2 Enforce separate maximum artifact and model-attempt budgets and exclude already successful extraction evidence.
- [x] 1.3 Add explicit eligibility and skip reason codes for candidate-present, no-evidence, disabled-budget, and exhausted states.

## 2. Grounded Recovery Integration

- [x] 2.1 Add a sparse recovery request path that requires explicit problem, choice, rationale or trade-off, and source quote evidence.
- [x] 2.2 Reuse normal candidate parsing, quote validation, source-ref persistence, confidence, and candidate review-state boundaries.
- [x] 2.3 Keep provider failures and ungrounded/null outputs non-fatal while preserving bounded rejection and loss reasons.
- [x] 2.4 Add sparse eligibility, attempt, evidence-family, recovered-candidate, rejection, and residual-loss counters to import summaries.

## 3. Automated Verification

- [x] 3.1 Test trigger and non-trigger conditions, deterministic family-diverse selection, and budget limits.
- [x] 3.2 Test grounded recovery candidate creation with source refs and candidate review state.
- [x] 3.3 Test null, invalid quote, malformed output, provider failure, and no-eligible-evidence outcomes.
- [x] 3.4 Test import-summary and fresh-rehearsal evidence metrics without changing successful normal extraction behavior.
- [x] 3.5 Run focused pytest, broader engine regression, and OpenSpec strict validation.

## 4. Real Repository Regression

- [x] 4.1 Select a previously unused public GitHub repository with explicit decision-rich artifacts and prove no-workspace preflight.
- [x] 4.2 Run a real fresh import with the configured model provider and capture sparse conversion evidence.
- [x] 4.3 Use Chrome browser and human-style interaction to verify dashboard, Review, candidate grounding, Why Search, and Drift.
- [x] 4.4 Compare the new result with the sniffio zero-candidate baseline and preserve warning/blocking boundaries.

## 5. Records And Closure

- [x] 5.1 Archive readiness evidence, screenshots, commands, model-call proof, limitations, and conversion metrics.
- [x] 5.2 Update the project log, completion taskbook, and next-development plan.
- [x] 5.3 Archive the OpenSpec change, rerun governance/strict checks, and commit only scoped files.
