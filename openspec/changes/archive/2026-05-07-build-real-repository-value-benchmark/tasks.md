## 1. Fixtures And Expectations

- [x] 1.1 Add repository role, benchmark purpose, and expected value outcome metadata to each curated repository fixture.
- [x] 1.2 Add or update fixture validation tests so offline validation requires repository roles, benchmark purpose, and bounded value outcome expectations.
- [x] 1.3 Review why and drift case fixtures against the curated repository roles and keep focused regression expectations bounded to status, citations, terms, primary-thread match, and forbidden alert types.

## 2. Value Classification

- [x] 2.1 Define bounded value outcome families for live benchmark rows, including useful, reviewable-limited, conversion-limited, evidence-limited, missing-workspace, and operational-blocked states.
- [x] 2.2 Implement value classification from dashboard readiness, candidate quality, accepted baseline, why-case results, drift-case results, and operational errors.
- [x] 2.3 Add unit tests for value classification across useful, reviewable-limited, conversion-limited, evidence-limited, missing-workspace, and operational-blocked examples.

## 3. Live Report Generation

- [x] 3.1 Extend the live real-repo JSON report with repository role, benchmark purpose, value outcome, key metrics, limitation categories, and follow-up categories.
- [x] 3.2 Add Markdown report generation derived from the same report structure as JSON.
- [x] 3.3 Add command-line options for Markdown report path and repository id filtering while preserving existing default behavior.
- [x] 3.4 Add tests proving Markdown output mirrors machine-readable rows and repo filtering does not affect offline fixture validation.

## 4. Documentation

- [x] 4.1 Document how to run offline fixture validation and live real-repository benchmark validation.
- [x] 4.2 Document value outcome families, operational versus product limitation handling, and why live benchmark results stay outside default CI.
- [x] 4.3 Record that generated live reports default to `.tmp/` and should be attached or summarized by operators instead of committed as stale evidence.

## 5. Validation

- [x] 5.1 Run benchmark fixture/eval tests covering fixture shape, value classification, JSON report fields, Markdown report output, and repo filtering.
- [x] 5.2 Run the offline benchmark validation command.
- [x] 5.3 Run OpenSpec validation for `build-real-repository-value-benchmark`.
- [x] 5.4 Run the local agent governance guardrail and record any caution or pause evidence before archiving.
