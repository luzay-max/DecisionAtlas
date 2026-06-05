## Context

Engine tests are stored under `services/engine/tests/`, but pytest's default discovery also collects root-level files matching `test_*.py`. Local debugging scripts currently exist under `services/engine/`, so `uv run pytest -q` can fail locally even when the intended engine suite is healthy.

## Goals / Non-Goals

**Goals:**
- Make `uv run pytest -q` from `services/engine/` discover only the canonical engine test suite.
- Preserve existing targeted test commands under `tests/...`.
- Document scratch-file placement so future debugging artifacts do not affect validation.

**Non-Goals:**
- Do not delete or rewrite existing local scratch files in this change.
- Do not change CI stages beyond making the existing pytest command deterministic.
- Do not change production engine behavior.

## Decisions

- Use pytest `testpaths = ["tests"]` in `services/engine/pyproject.toml`.
  - Rationale: this keeps the current command contract intact while narrowing discovery to the intended suite.
  - Alternative considered: update every script and workflow to call `pytest tests -q`; rejected because the root command would remain unsafe for developers.
- Keep `.tmp/` as the standard scratch location.
  - Rationale: the repository already ignores `.tmp/` and release/readiness docs already treat it as non-durable scratch output.
- Avoid moving untracked scratch files automatically.
  - Rationale: untracked files may contain one-off local evidence or credentials; relocating them without explicit review could be more risky than adding safe discovery boundaries.

## Risks / Trade-offs

- Root-level engine test files will no longer run by default -> Require real tests to live under `services/engine/tests/`.
- Developers may still create scratch files in package roots -> Document the convention and rely on pytest discovery boundaries to prevent validation drift.
- Some old docs reference broad pytest behavior -> Keep command unchanged and clarify discovery instead of mass-editing historical plans.
