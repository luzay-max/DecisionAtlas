## 1. Current Hosted Preview Audit

- [x] 1.1 Audit existing hosted operator docs, deployment docs, quick start, demo script, release notes, and validation reports for hosted preview readiness gaps.
- [x] 1.2 Audit `scripts/demo` health, smoke, reset, and reseed commands to confirm current arguments and expected hosted/local behavior.
- [x] 1.3 Audit guided demo and imported-lane copy to confirm the seeded public walkthrough remains distinct from optional real-repo/admin lanes.

## 2. Hosted Preview Documentation

- [x] 2.1 Create or update a concise hosted preview readiness checklist with required services, environment variables, validation commands, and pass/fail categories.
- [x] 2.2 Update hosted operator or deployment docs with external preview bring-up, health/smoke, reset/reseed, and troubleshooting flow.
- [x] 2.3 Add an external walkthrough script that starts with the seeded demo and frames imported/GitHub App/private repo lanes as optional bounded demonstrations.
- [x] 2.4 Ensure release-facing docs describe hosted preview readiness as post-RC confidence, not as the canonical release gate.

## 3. Verification Report

- [x] 3.1 Create or update a hosted preview readiness report that records commit, environment assumptions, commands, observed results, status, known limitations, and follow-ups.
- [x] 3.2 Record whether external hosted health/smoke/reset/reseed checks were run, unavailable, or rehearsed locally.
- [x] 3.3 Record any blocking issue separately from non-blocking limitations before claiming preview readiness.

## 4. Script Or Product Copy Fixes

- [x] 4.1 Make minimal script fixes only if audit or verification reveals broken hosted-preview command behavior.
- [x] 4.2 Make minimal web copy fixes only if the guided-demo versus imported-lane boundary is unclear for external preview use.
- [x] 4.3 Preserve existing release gate behavior and avoid adding live hosted checks to default CI.

## 5. Tests And Validation

- [x] 5.1 Run targeted docs/script checks or tests for any files changed during implementation.
- [x] 5.2 Run hosted operator commands that are safe in the current environment, or record why they are operator-guided/unavailable.
- [x] 5.3 Run OpenSpec validation for `prepare-v0-3-hosted-preview`.
- [x] 5.4 Run broader validation such as `openspec validate --all --strict` or release-facing checks if implementation touches shared release/docs paths.
