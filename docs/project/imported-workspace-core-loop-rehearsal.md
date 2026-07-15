# Imported Workspace Core Loop Rehearsal

This rehearsal verifies the core DecisionAtlas loop for a real imported workspace:

`public GitHub repository -> imported workspace -> dashboard -> review -> why-search -> drift -> guardrail`

## Collector Command

Use an existing public import rehearsal artifact:

```powershell
python scripts\ci\collect_imported_workspace_core_loop.py `
  --import-rehearsal-json .tmp\public-github-import-rehearsal.json `
  --guardrail-json .tmp\agent-guardrail-summary.json `
  --output-json .tmp\imported-workspace-core-loop-rehearsal.json `
  --output-markdown .tmp\imported-workspace-core-loop-rehearsal.md
```

Or run against an explicit workspace:

```powershell
python scripts\ci\collect_imported_workspace_core_loop.py `
  --repo pallets/flask `
  --workspace-slug github-pallets-flask `
  --run-guardrail `
  --output-json .tmp\imported-workspace-core-loop-rehearsal.json `
  --output-markdown .tmp\imported-workspace-core-loop-rehearsal.md
```

## Browser Rehearsal

```powershell
pnpm --filter @decisionatlas/web exec playwright test imported-workspace-core-loop.spec.ts --config playwright.config.ts --reporter=line
```

The browser rehearsal creates or reuses a public GitHub workspace for `pallets/flask`, then walks dashboard, review, why-search, drift, and evidence surfaces.

## Evidence Boundary

- The collector records compact lane statuses and counts only.
- The browser rehearsal uses a real public GitHub repository workspace but mocks the why-search answer for deterministic UI validation.
- Live repository import quality and multi-repo trend quality remain covered by benchmark/readiness evidence.
- Guardrail evidence is advisory and must not be treated as a correctness proof by itself.
