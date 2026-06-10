## 1. Private-Repo Evidence Materials

- [x] 1.1 Add a customer-safe private-repo pilot evidence template under `docs/project/`.
- [x] 1.2 Add a committed operator-guided sample JSON/Markdown evidence pair that contains no private source content or credentials.
- [x] 1.3 Update pilot delivery, self-hosted commercial baseline, and related customer-facing materials to reference sanitized private-repo evidence.

## 2. Verification Tooling

- [x] 2.1 Add a local verifier script that validates private-repo pilot evidence JSON/Markdown structure and safety statements.
- [x] 2.2 Add tests covering passing operator-guided evidence, missing required statements, and obvious secret/token leakage.
- [x] 2.3 Include the private-repo evidence template in pilot kit and self-hosted package verification expectations.

## 3. Evidence Integration

- [x] 3.1 Ensure generated verifier output can be consumed as bounded handoff/readiness evidence.
- [x] 3.2 Generate `.tmp` JSON/Markdown verifier evidence from the committed sample.
- [x] 3.3 Record this change in the 2026-06-10 update log with validation commands and limitations.

## 4. Validation

- [x] 4.1 Run targeted verifier and existing pilot/package verification tests.
- [x] 4.2 Run OpenSpec strict validation for the change and all specs.
- [x] 4.3 Use browser/Chromium to render the Markdown private-repo evidence material and confirm readability.
- [x] 4.4 Run or reuse a random public GitHub repository evidence check as a non-sensitive stand-in for the live-repo validation habit, while preserving that it is not private-repo proof.
- [x] 4.5 Run the governance guardrail and record the result in the handoff.
