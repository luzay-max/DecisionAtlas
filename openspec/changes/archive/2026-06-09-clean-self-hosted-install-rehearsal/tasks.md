## 1. Clean Rehearsal Collector

- [x] 1.1 Add `scripts/ci/rehearse_clean_self_hosted_install.py` with CLI arguments for package path, label, version label, output path, optional evidence inputs, and optional live stack URLs.
- [x] 1.2 Implement isolated scratch package copy under `.tmp/clean-self-hosted-install/<label>/` with safety checks that prevent deleting paths outside that owned directory.
- [x] 1.3 Implement required package asset checks for manifest, README, environment template, self-hosted docs, startup launcher, verifier entry point, license boundary, and handoff documentation.
- [x] 1.4 Implement source evidence ingestion that preserves `pass`, `warning`, `blocking`, `operator_guided`, `not_provided`, `known_limitation`, and local stack failure states.
- [x] 1.5 Generate deterministic JSON and operator-readable Markdown reports at `.tmp/clean-self-hosted-install-rehearsal.json/md`.

## 2. Integration Updates

- [x] 2.1 Update self-hosted package README/package guide/runbook references so operators can run clean install rehearsal and understand expected outputs.
- [x] 2.2 Update package verification notes to identify clean install rehearsal as a separate customer-readiness evidence lane.
- [x] 2.3 Update team handoff report generation so clean install rehearsal evidence can be included or explicitly marked missing.

## 3. Tests

- [x] 3.1 Add pytest coverage for successful clean rehearsal report generation against a synthetic package.
- [x] 3.2 Add pytest coverage for missing package or missing required asset producing `blocking`.
- [x] 3.3 Add pytest coverage for optional evidence statuses being preserved rather than converted to pass.
- [x] 3.4 Add pytest coverage for team handoff report clean install evidence inclusion and missing-evidence behavior.

## 4. Real Rehearsal Evidence

- [x] 4.1 Build and verify a self-hosted package from the current workspace.
- [x] 4.2 Run clean install rehearsal against that package and generate JSON/Markdown evidence.
- [x] 4.3 Run or reuse release evidence, hosted readiness, benchmark comparison, readiness history, public GitHub import, package verification, license boundary, and handoff evidence as available.
- [x] 4.4 Use browser-based operator review to open the generated Markdown report and confirm it is readable without a backend.

## 5. OpenSpec, Docs, and Validation

- [x] 5.1 Sync final requirements into main specs after implementation.
- [x] 5.2 Record the 2026-06-09 update log entry for clean self-hosted install rehearsal.
- [x] 5.3 Run targeted pytest and `openspec validate --all --strict`.
- [x] 5.4 Archive `clean-self-hosted-install-rehearsal`, commit, push, and verify CI.
