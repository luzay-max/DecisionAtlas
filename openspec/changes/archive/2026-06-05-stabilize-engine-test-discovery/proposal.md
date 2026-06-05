## Why

Engine validation currently relies on `uv run pytest -q`, but local scratch files named `test_*.py` under `services/engine/` can be collected as tests and cause false failures. This weakens the default development protocol and makes local verification less reliable than CI intent.

## What Changes

- Constrain engine pytest discovery to the canonical `tests/` directory.
- Document that ad hoc debugging scripts and generated reports belong in `.tmp/` or another ignored scratch location, not package roots.
- Keep existing canonical test commands working while preventing accidental root-level scratch collection.

## Capabilities

### New Capabilities
- `engine-test-discovery`: Defines stable engine test discovery boundaries and scratch-output hygiene for local and CI validation.

### Modified Capabilities
- None.

## Impact

- Affects `services/engine/pyproject.toml` pytest configuration.
- May update developer documentation or release checklist references for scratch-file hygiene.
- Does not change production APIs, database schema, or runtime behavior.
