## 1. Fixture Model

- [x] 1.1 Add focused why-case fixtures for at least the `browser-use/browser-use` imported workspace.
- [x] 1.2 Add drift expectation fixtures for known implementation-heavy follow-up patterns that must stay out of strong replacement paths.
- [x] 1.3 Ensure sparse or conversion-limited repository expectations remain represented for `n8n-io/n8n`.

## 2. Benchmark Validation

- [x] 2.1 Extend `scripts/ci/run_benchmark.py` to validate the new case fixture shape in default offline mode.
- [x] 2.2 Add optional live execution support for real-repo why cases against an already-running local API and existing imported workspace.
- [x] 2.3 Report benchmark failures with case id, workspace slug, observed status, and expected broad outcome.

## 3. Tests and Documentation

- [x] 3.1 Add tests that fail on malformed repository, why-case, or drift-case benchmark fixtures.
- [x] 3.2 Update `real-repository-validation-baseline.md` to point to the fixture-backed benchmark cases.
- [x] 3.3 Run `python scripts/ci/run_benchmark.py` and targeted benchmark tests.
