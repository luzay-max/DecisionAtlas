## Why

DecisionAtlas now has a stable local guided demo lane, a bounded imported real-repository lane, and repeatable release validation, but it still lacks an operator-grade hosted demo flow. The current deployment docs explain how to bring services up, yet they do not define a clear hosted environment contract, recovery path, or lane-isolation guidance for demo operators.

## What Changes

- Define a hosted-demo operator contract that names the required environment variables, service boundaries, and backend-only secret handling rules.
- Add a canonical hosted-demo health and smoke flow so operators can verify the stack and the stable walkthrough without rediscovering commands.
- Add a bounded reset and reseed flow for recovering the demo workspace and the single-machine demo environment.
- Document how the guided demo workspace stays isolated from imported workspaces so the hosted walkthrough does not drift into ad hoc real-repo operations.

## Capabilities

### New Capabilities
- `hosted-demo-operator-flow`: Defines the hosted demo environment contract, operator checks, recovery flow, and demo/imported lane isolation.

### Modified Capabilities

## Impact

- Affected docs: deployment, quick start, demo script, FAQ, and operator-facing project notes.
- Affected scripts: hosted demo health/smoke wrappers plus reset/reseed helpers.
- Affected systems: web, api, engine, PostgreSQL, Redis, and hosted environment variable handling.
