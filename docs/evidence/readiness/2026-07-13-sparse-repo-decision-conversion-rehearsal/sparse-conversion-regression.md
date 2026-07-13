# Sparse Repository Decision Conversion Regression

- Generated at: `2026-07-13T10:44:59.2577184+08:00`
- Status: `warning`
- Baseline: `python-trio/sniffio` · candidates `0` · accepted `0`
- Current: `jazzband/pip-tools` · candidates `28` · accepted `1`
- Candidate delta: `28`
- Current Why: `pass` · citations `2`
- Current Drift: `pass` / `clean`
- Current sparse lane: `skipped` / `candidate_present` · model attempts `0`

## Supplemental Sparse Branch

- Repository: `python-trio/sniffio`
- Status: `exhausted`
- Eligible artifacts: `4`
- Model attempts: `4`
- Recovered candidates: `0`
- Rejections: `{"null_decision":4}`

## Limitations

- Repository profiles differ, so candidate delta is evidence rather than a controlled causal estimate.
- pip-tools normal extraction produced candidates, so sparse recovery correctly skipped with zero extra calls.
- The supplemental sniffio run proves the sparse branch executed four model attempts and preserved zero candidates when all outputs were null.
- Current candidates are model-extracted review items; only one was manually accepted after evidence inspection.
