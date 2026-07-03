# Multi-Repo Live Diagnosis Rotation

This rehearsal rotates through real public GitHub repository identities and collects compact evidence for the import plus imported-workspace core loop.

## Commands

Run a deterministic random sample from the fixed trend pool:

```powershell
python scripts\ci\collect_multi_repo_live_diagnosis.py `
  --random-count 3 `
  --random-seed 13 `
  --output-json .tmp\multi-repo-live-diagnosis.json `
  --output-markdown .tmp\multi-repo-live-diagnosis.md
```

Run explicit repositories:

```powershell
python scripts\ci\collect_multi_repo_live_diagnosis.py `
  --repo-id httpx `
  --repo-id fastapi `
  --repo-id rich `
  --output-json .tmp\multi-repo-live-diagnosis.json `
  --output-markdown .tmp\multi-repo-live-diagnosis.md
```

Optional live-depth flags:

```powershell
python scripts\ci\collect_multi_repo_live_diagnosis.py `
  --repo-id fastapi `
  --wait-import `
  --evaluate-drift `
  --run-guardrail `
  --output-json .tmp\multi-repo-live-diagnosis.json `
  --output-markdown .tmp\multi-repo-live-diagnosis.md
```

## Evidence Boundary

- The pool contains real public repository identities, not private source code.
- Reports store statuses, counts, bounded reasons, and next actions.
- Reports must not include GitHub tokens, private repository contents, raw model output, or unbounded local paths.
- `provider_failure`, `local_stack_failure`, `operator_guided`, `warning`, and `not_provided` are valid evidence states, not hidden failures.

## How To Read Results

- `pass`: selected repositories produced clean enough setup and core-loop evidence.
- `warning`: at least one repository has partial evidence, weak candidates, drift uncertainty, missing guardrail input, or operator-guided setup.
- `blocking`: at least one selected repository cannot be diagnosed because the local stack, GitHub provider, or import path failed.

The output is meant to feed release rehearsal and readiness history. It does not replace benchmark comparison evidence; it proves whether real repository workspaces can be diagnosed across a rotating sample.
