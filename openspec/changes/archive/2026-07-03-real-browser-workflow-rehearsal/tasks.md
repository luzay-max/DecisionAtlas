## 1. Browser Workflow Coverage

- [x] 1.1 Add a Playwright human workflow rehearsal that starts from homepage onboarding and reaches workspace, review, why-search, drift, evidence, and team role checks.
- [x] 1.2 Include a real public GitHub repository reference in the rehearsal and assert it remains visible where repository/import context is shown.
- [x] 1.3 Keep mocked or seeded API lanes explicit so browser proof is not confused with live GitHub import proof.

## 2. Documentation And Evidence

- [x] 2.1 Document how to run the real browser workflow rehearsal locally.
- [x] 2.2 Record the rehearsal scope, command, result, and limitations in the project update log.
- [x] 2.3 Add or update spec files so the browser rehearsal requirements survive archival.

## 3. Validation

- [x] 3.1 Run the new Playwright rehearsal against the local smoke or real stack.
- [x] 3.2 Run related web unit/browser tests needed to prove the interaction flow did not regress.
- [x] 3.3 Run OpenSpec strict validation for the change and all specs.
