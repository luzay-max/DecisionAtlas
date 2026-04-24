## 1. Extend live benchmark reporting

- [ ] 1.1 Review current live benchmark fixtures and API payloads for dashboard readiness, why answers, and drift evaluation/listing.
- [ ] 1.2 Extend `scripts/ci/run_benchmark.py` live real-repo mode to collect repo-level dashboard/readiness observations for each curated workspace.
- [ ] 1.3 Add a structured report writer for live real-repo validation results, including bounded outcome, counts, why status, drift status, and operational failure notes.

## 2. Validate broad live outcomes

- [ ] 2.1 Compare observed readiness states against each repo's allowed `expected_readiness_states` without asserting exact answer prose.
- [ ] 2.2 Preserve and integrate focused `browser-use` why-case checks with citation and status floors in the report.
- [ ] 2.3 Validate drift cases or drift-state outcomes for curated workspaces and report forbidden strong replacement outcomes explicitly.
- [ ] 2.4 Classify missing workspaces, unreachable API, provider/network failures, and unavailable local state as operational outcomes distinct from product evidence limitations.

## 3. Protect offline behavior

- [ ] 3.1 Keep default `python scripts/ci/run_benchmark.py` fixture validation provider-independent and free of live API calls.
- [ ] 3.2 Add or update tests for fixture validation, live result classification, and report generation.
- [ ] 3.3 Confirm `scripts/ci/pre-release.ps1` continues to use only the offline benchmark path.

## 4. Document and verify

- [ ] 4.1 Update `docs/project/real-repository-validation-baseline.md` with the live validation workflow, report fields, and interpretation rules.
- [ ] 4.2 Run offline benchmark validation and targeted tests for the changed benchmark code.
- [ ] 4.3 If a suitable local stack and imported workspaces are available, run `python scripts/ci/run_benchmark.py --live-real-repos` and record observed outcomes; otherwise record the operational preconditions that blocked live execution.
