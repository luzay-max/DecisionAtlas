## Why

DecisionAtlas now has many validated backend, evidence, and self-hosted delivery paths, but the most important product claim still needs stronger browser-level proof: a human operator can start from the UI, move through workspace, team, review, why-search, drift, and evidence flows, and connect that to a real GitHub repository signal.

This change turns browser/UI validation from scattered smoke checks into a repeatable human workflow rehearsal aligned with the current self-hosted product direction.

## What Changes

- Add a real browser workflow rehearsal that exercises the main product path through the Web UI.
- Require the rehearsal to use a real public GitHub repository reference or import fixture, not only seeded demo copy.
- Capture browser-level evidence for homepage onboarding, workspace context, review, why-search, drift, evidence center, and team permission flow.
- Preserve non-clean states such as unavailable live import, missing credentials, or operator-guided lanes instead of presenting them as pass.
- Keep the rehearsal local and safe: no git push, no destructive reset, no secret capture, and no private repo content in evidence.

## Capabilities

### New Capabilities

- `real-browser-workflow-rehearsal`: Defines a browser-driven human workflow rehearsal that records UI-level proof for the DecisionAtlas core product path.

### Modified Capabilities

- `workspace-interaction-flow`: Requires the main UI flow to be verifiable through browser-level navigation and next-action continuity.
- `mimo-ui-smoke-coverage`: Expands smoke coverage expectations from static page checks to cross-page human workflow rehearsal.
- `live-repository-analysis`: Requires real public repository references used in UI rehearsal evidence to remain explicit and distinguish live import from mocked or seeded responses.

## Impact

- `apps/web/tests-e2e/`: Add or update Playwright coverage for the end-to-end human workflow.
- `docs/project/`: Add operator-facing rehearsal notes and update log evidence.
- `openspec/specs/`: Add and update specs so future UI/product changes keep the rehearsal path intact.
- No API breaking changes expected.
