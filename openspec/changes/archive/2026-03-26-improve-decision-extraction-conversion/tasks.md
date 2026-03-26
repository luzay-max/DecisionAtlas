## 1. Artifact-Aware Full Extraction

- [x] 1.1 Add a small artifact-family classifier for screened-in extraction inputs, covering rationale docs, high-signal PRs, and lighter-weight issue/commit evidence
- [x] 1.2 Introduce artifact-family-aware full extraction prompts or prompt variants without reopening shortlist or screening scope
- [x] 1.3 Verify that the selected extraction family is recorded in run diagnostics for later analysis

## 2. Candidate Salvage And Parsing

- [x] 2.1 Refactor full extraction parsing so recoverable structured outputs can be normalized instead of being dropped immediately
- [x] 2.2 Define and enforce conservative salvage rules for what counts as enough grounded decision structure to persist a candidate
- [x] 2.3 Record categorized conversion-loss reasons for screened-in artifacts that still do not become candidates

## 3. Imported Outcome Diagnostics

- [x] 3.1 Extend extraction summaries and imported workspace read models with candidate-yield and conversion-loss counters
- [x] 3.2 Update imported dashboard and readiness messaging to distinguish evidence-limited runs from conversion-limited runs
- [x] 3.3 Preserve compatibility with existing import-stage and outcome surfaces while adding the richer diagnostics

## 4. Validation

- [x] 4.1 Add engine tests for artifact-family routing, salvage behavior, and conversion-loss categorization
- [x] 4.2 Add UI and API tests for conversion-limited imported workspace summaries
- [x] 4.3 Re-run curated real-repository validation with candidate-yield comparisons for the repos that previously showed screened-in but zero-candidate outcomes
