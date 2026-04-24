## 1. Operator Contract And Docs

- [x] 1.1 Define the hosted-demo environment contract in deployment and quick-start docs, including required services, required variables, optional live-provider settings, and backend-only secret handling.
- [x] 1.2 Add an operator-facing hosted demo guide that explains demo lane vs imported lane isolation, hosted verification steps, and when to use reset versus reseed.
- [x] 1.3 Keep the English and Chinese operator-facing docs aligned on the same hosted-demo commands, boundaries, and recovery meaning.

## 2. Operator Scripts And Checks

- [x] 2.1 Add a canonical hosted-demo health check script that verifies web, api, engine, and required dependency reachability in an operator-readable way.
- [x] 2.2 Add a canonical hosted-demo smoke check wrapper that verifies the stable guided walkthrough path and clearly separates any optional imported verification.
- [x] 2.3 Add bounded reset and reseed helper scripts for restoring the seeded demo lane without making imported-workspace cleanup the default action.

## 3. Validation

- [x] 3.1 Add script-level tests or verification coverage for the new hosted-demo health, smoke, reset, and reseed paths where practical.
- [x] 3.2 Run the hosted-demo operator flow locally and record the validated command path in the operator docs.
