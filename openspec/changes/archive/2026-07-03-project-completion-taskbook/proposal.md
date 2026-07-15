## Why

DecisionAtlas has accumulated many OpenSpec changes, evidence scripts, browser rehearsals, and commercialization plans. The remaining risk is execution drift: future work can easily repeat completed items or skip weakly proven items because there is no single taskbook that maps plan goals to evidence.

This change creates a living completion taskbook that guides future development until the project reaches a complete self-hosted product loop.

## What Changes

- Add a project completion taskbook that maps current plan goals to implementation/evidence status.
- Add a verification matrix for core loop, governance, real repository validation, self-hosted delivery, commercial readiness, browser workflow, and documentation.
- Identify next OpenSpec change candidates in priority order.
- Record which items are complete, which are partially proven, and which still need stronger evidence.
- Keep the taskbook aligned with OpenSpec archival, tests, and update logs.

## Capabilities

### New Capabilities

- `project-completion-taskbook`: Defines a living taskbook for tracking completion status, evidence, gaps, and next changes toward a complete DecisionAtlas product loop.

### Modified Capabilities

- `final-development-roadmap`: Requires future roadmap updates to reference the taskbook and distinguish complete, partial, and unverified claims.

## Impact

- Adds `docs/plans/2026-07-03-decisionatlas-completion-taskbook.md`.
- Updates planning discipline around OpenSpec archived changes and validation evidence.
- No product API or runtime behavior changes.
