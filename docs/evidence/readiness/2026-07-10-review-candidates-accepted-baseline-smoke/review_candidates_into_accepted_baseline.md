# Review Candidates Into Accepted Baseline

- Generated at: `2026-07-10T09:14:16.0717494+08:00`
- Status: `pass`
- Mode: `confirmed_accept`
- Workspace: `github-textualize-rich`
- Max accept: `1`
- Before: `{"accepted_count": 0, "candidate_count": 35}`
- After: `{"accepted_count": 1, "candidate_count": 34}`
- Next action: `rerun_core_loop_baseline_evidence`

## Selected Candidates

| ID | Title | Review state | Confidence |
| --- | --- | --- | --- |
| 241 | Don't use windows legacy terminal support when ctypes is not available | candidate | 0.95 |

## Accepted Decisions

- `241` Don't use windows legacy terminal support when ctypes is not available

## Errors

- None

## Limitations

- Dry-run mode does not mutate review state.
- Confirmed mode accepts only the bounded candidate prefix returned by the existing review API order.
- This evidence stores decision IDs/titles and bounded metadata only; do not include secrets or raw private source.
