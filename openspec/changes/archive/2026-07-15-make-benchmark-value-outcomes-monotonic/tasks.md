## 1. Monotonic Benchmark Value Assessment

- [x] 1.1 Add a pure value-outcome assessment helper that preserves the existing rank and distinguishes exact match, `exceeds_floor`, `below_floor`, operational, and unconstrained cases.
- [x] 1.2 Update `_attach_value_summary` to use the helper, emit the minimum product-value floor and bounded assessment, and keep operational outcomes non-promotable.

## 2. Regression Tests And Fixture Coverage

- [x] 2.1 Add deterministic tests for a stronger-than-expected outcome, a below-floor outcome, missing workspace, operational failure, and profiles with only operational expectations.
- [x] 2.2 Add a live-style benchmark regression fixture proving the current n8n metrics classify as allowed without changing candidate, Why, Drift, or screened-in gates.

## 3. Real Verification And Evidence

- [x] 3.1 Run focused benchmark tests, full engine tests, Node tests, typecheck, benchmark fixture validation, and OpenSpec strict validation.
- [x] 3.2 Rerun the fixed live real-repository benchmark against the running stack and generate current JSON/Markdown plus snapshot/comparison evidence; preserve any genuine failures.
- [x] 3.3 Run real Chrome navigation for the affected benchmark workspace and record the bounded value/readiness result without changing product data.

## 4. Closeout

- [x] 4.1 Generate release evidence and readiness-history entry for the benchmark correction, update the taskbook, dated update log, and next-development plan.
- [ ] 4.2 Archive the OpenSpec change, commit scoped files, push the dedicated branch, run and inspect GitHub Actions, and report the final CI result.
