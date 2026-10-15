## Why

The fresh `python-trio/sniffio` rehearsal imported 147 real artifacts and screened in decision-like evidence, yet produced zero candidates because the only extraction resolved to `null_decision`. The import path is reliable, but sparse repositories still fail to reach the reviewable decision baseline that powers Why Search and Drift.

## What Changes

- Add bounded sparse-repository recovery when normal screening/extraction produces no candidates despite high-signal artifacts.
- Improve candidate selection across PR, commit, issue, and repository-document evidence while preserving deterministic budgets.
- Require every recovered candidate to pass the existing grounded quote, source-reference, confidence, and review-state boundaries.
- Record conversion attempts, recovery reasons, accepted/rejected evidence, and residual `null_decision` outcomes without treating zero candidates as import failure.
- Add deterministic fixtures and live fresh-repository regression evidence that compares candidate yield without automatically accepting decisions.

## Capabilities

### New Capabilities

- `sparse-repo-decision-conversion`: Defines bounded sparse-repository fallback selection, grounded recovery, quality gates, observability, and real-repository regression evidence.

### Modified Capabilities

- `decision-extraction-conversion`: Extraction conversion shall distinguish eligible sparse-repository recovery from ordinary null-decision loss and expose bounded conversion counters.
- `fresh-public-repo-import-rehearsal`: Fresh import evidence shall report sparse conversion attempts and candidate yield so future rehearsals can compare core-loop readiness honestly.

## Impact

- Primarily affects `services/engine/app/jobs/import_jobs.py`, extraction helpers/providers, import summaries, and focused engine tests.
- Extends fresh-import and readiness evidence with compact conversion metrics; no public API break is intended.
- Live validation requires a running real stack, configured model provider, and a previously unused public GitHub repository.
