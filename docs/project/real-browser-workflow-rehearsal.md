# Real Browser Workflow Rehearsal

This rehearsal verifies the customer-visible DecisionAtlas workflow in a real browser:

- Homepage onboarding and repository import guidance.
- Real public GitHub repository context using `openai/openai-cookbook`.
- Demo workspace navigation into review, why-search, drift, and evidence.
- Team account creation and reviewer/viewer permission separation.

## Command

```powershell
pnpm --filter @decisionatlas/web exec playwright test real-browser-workflow-rehearsal.spec.ts --config playwright.config.ts --reporter=line
```

The Playwright config starts the smoke engine, API, and Web services unless `PLAYWRIGHT_SKIP_WEBSERVER=1` is set.

## Evidence Boundary

The browser rehearsal uses a mocked import lookup response for `openai/openai-cookbook` so the UI flow is deterministic and does not depend on GitHub availability or credentials.

This proves product interaction continuity. It does not replace live repository import evidence, benchmark comparison evidence, release evidence, or readiness history.

## Local Notes

If localhost checks are routed through a local proxy, clear proxy variables or bypass localhost before running the browser rehearsal.

If Docker or the smoke stack is already running, use the standard Playwright config or set `PLAYWRIGHT_SKIP_WEBSERVER=1` only when Engine, API, and Web are already reachable.
