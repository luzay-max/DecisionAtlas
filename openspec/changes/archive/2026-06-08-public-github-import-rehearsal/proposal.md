## Why

The latest live repository benchmark generated explicit `missing_workspace` evidence for `fastapi/fastapi`, which means the public repository was selected but not imported into the local self-hosted workspace before validation. This change closes that gap by making public GitHub repository import and post-import benchmark evidence a repeatable rehearsal lane.

## What Changes

- Add a repeatable public GitHub import rehearsal for a curated public repository, starting with `fastapi/fastapi`.
- Ensure the rehearsal can create or reuse the expected workspace before benchmark validation runs.
- Record bounded outcomes for import, workspace readiness, and benchmark comparison so a missing workspace is treated as operator setup unless the rehearsal imports it successfully.
- Update self-hosted delivery evidence guidance so public-repo benchmark claims require either imported-workspace proof or an explicit non-pass limitation.
- No breaking changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `live-repository-analysis`: Require public GitHub rehearsal flows to create or reuse a workspace before claiming benchmark evidence for that repository.
- `lightweight-real-repo-benchmarks`: Require benchmark comparison evidence to distinguish selected-but-not-imported repositories from imported repositories with analyzable results.
- `imported-workspace-readiness-surface`: Require readiness evidence to expose whether a public repository workspace exists, was imported, or remains operator-guided.

## Impact

- Affected code: import/rehearsal scripts, benchmark runner integration, readiness evidence documentation, and tests around import/workspace/benchmark status.
- Affected systems: local self-hosted rehearsal, `.tmp` generated evidence, and durable readiness evidence history.
- No new external service dependency beyond the existing public GitHub access path already used by live benchmark configuration.
