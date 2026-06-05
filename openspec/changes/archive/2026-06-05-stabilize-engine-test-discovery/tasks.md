## 1. Test Discovery Configuration

- [x] 1.1 Add pytest `testpaths` configuration so default engine pytest discovers only `tests/`
- [x] 1.2 Verify `uv run pytest -q` ignores root-level scratch `test_*.py` files

## 2. Scratch Hygiene Documentation

- [x] 2.1 Document that temporary debugging scripts and generated local reports belong in `.tmp/`
- [x] 2.2 Keep existing historical release evidence guidance consistent with `.tmp/` as scratch output

## 3. Validation

- [x] 3.1 Run engine pytest from `services/engine/`
- [x] 3.2 Run repository typecheck or targeted validation affected by this change
