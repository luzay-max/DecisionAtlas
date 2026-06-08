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
