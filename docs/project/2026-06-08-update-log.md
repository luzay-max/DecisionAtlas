# 2026-06-08 Update Log

## Public GitHub Import Rehearsal

- Continued OpenSpec change `public-github-import-rehearsal`.
- Added `scripts/ci/rehearse_public_github_import.py` to convert a curated public GitHub repository from selected benchmark input into explicit import/reuse setup evidence.
- Added offline script tests for reused workspace, missing workspace import creation, waiting for an existing active import, local-stack failure, and operator-guided access requirements.
- Ran real local-stack rehearsal for `fastapi/fastapi`.

## Real Evidence

- Public import rehearsal output:
  - JSON: `.tmp/public-github-import-rehearsal.json`
  - Markdown: `.tmp/public-github-import-rehearsal.md`
  - Repository: `fastapi/fastapi`
  - Workspace: `github-fastapi-fastapi`
  - Setup outcome: `reused`
  - Benchmark ready: `true`
  - Import job: `8823fe6a-bd3b-4cef-b243-9c6d1fdc5c23`
  - Import status: `succeeded`
  - Imported count: `2543`

- Model-backed extraction evidence from the import job:
  - `full_extraction_requests`: `21`
  - `completed_full_extractions`: `21`
  - `screened_in_artifacts`: `13`
  - `created_candidates`: `8`
  - `salvaged_candidates`: `7`
  - `recovered_candidates`: `3`
  - `average_full_extraction_latency_ms`: `20841`

- Live real-repo benchmark output:
  - JSON: `.tmp/fastapi-live-real-repo-validation-report.json`
  - Markdown: `.tmp/fastapi-live-real-repo-validation-report.md`
  - Result: passed
  - Bounded outcome: `review_ready`
  - Value outcome: `useful_now`
  - Candidate decisions: `8`
  - Strong candidates: `1`
  - Thin candidate ratio: `0.0`
  - Follow-up categories: none

## Validation

- `python -m uv run pytest tests/ci/test_public_github_import_rehearsal.py -q`: `5 passed`
- `openspec validate public-github-import-rehearsal --type change --strict`: passed

## Notes

- An earlier benchmark attempt on 2026-06-08 failed with `operational_failure` because `127.0.0.1:3001` was not running. After the user restarted the local stack, Web/API/Engine health probes returned 200 and the benchmark passed.
- The DeepSeek cost chart showing `<¥0.01` is consistent with the import job's 21 completed model extraction requests.

## Multi Git Source Token Import

- Started OpenSpec change `multi-git-source-token-import`.
- Added provider/access-mode metadata to repository lookup and token-backed access-source responses.
- Added `/imports/git-sources/bind` as an admin-only provider-aware setup endpoint.
- Preserved implemented GitHub token setup by delegating to the existing private access binding path.
- Added bounded outcomes for recognized but not-yet-implemented sources:
  - GitLab/Gitee token setup returns `provider_unsupported` and `plan_provider_importer`.
  - Local path setup returns `local_path_unavailable` / `operator_guided` without echoing raw server paths.
- Updated the private repository access panel to show Git provider and access mode controls while keeping token material write-only.
- Synced OpenSpec main specs for `git-source-token-import`, `live-repository-analysis`, `imported-workspace-readiness-surface`, and `private-repo-access-product-flow`.

## Multi Git Source Validation

- `python -m uv run pytest tests/api/test_imports.py -q`: `20 passed`
- `pnpm --filter @decisionatlas/api test -- imports-route`: `9 passed`
- `pnpm --filter @decisionatlas/api typecheck`: passed
- `pnpm --filter @decisionatlas/web test -- private-repo-access-panel`: `6 passed`
- Browser/operator rehearsal on the running local stack:
  - Web/API health probes returned 200.
  - After expanding advanced controls, the admin setup surface rendered provider options `github`, `gitlab`, `gitee`, `local` and access modes `token`, `public`, `local_path`.
  - Initial real GitLab setup submission was blocked by a stale running Engine process returning `404 {"detail":"Not Found"}` from `/imports/git-sources/bind`.
  - After restarting the real stack, GitLab token setup returned `provider_unsupported` with `plan_provider_importer`; the submitted token was cleared and not rendered.
  - Local path setup returned `local_path_unavailable` with `configure_server_local_path_import`; the browser surface showed server-operator-guided status.
