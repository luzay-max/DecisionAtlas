# 2026-06-05 Update Log

## Test Discovery Stabilization

- Added OpenSpec change `stabilize-engine-test-discovery` to formalize engine pytest discovery boundaries and scratch-output hygiene.
- Constrained engine pytest discovery to `services/engine/tests/` via `services/engine/pyproject.toml`.
- Updated the release checklist to keep temporary debugging scripts, generated local reports, and ad hoc validation artifacts in `.tmp/` or another ignored scratch location.
- Verified `uv run pytest --collect-only -q` from `services/engine/` collects only the canonical test suite and ignores root-level scratch `test_*.py` files.
- Moved existing untracked local scratch files into `.tmp/local-scratch/2026-06-05/` so they remain available locally without polluting Git status or pytest discovery.

## Validation

- `python -m uv run pytest --collect-only -q` from `services/engine/`: `247 tests collected`
- `python -m uv run pytest -q` from `services/engine/`: `247 passed`
- `pnpm typecheck`: passed
- `openspec validate stabilize-engine-test-discovery --type change --strict`: passed

## Notes

- Existing untracked local scratch files were intentionally preserved under ignored `.tmp/` storage and not committed.
- Browser/Chrome-based UI verification was not required for this configuration-only change; it remains required for the next UI-facing self-hosted/team workflow changes.
