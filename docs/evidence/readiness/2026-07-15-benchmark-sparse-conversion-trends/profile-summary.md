# Benchmark Sparse Conversion Trends Live Evidence

- Generated: `2026-07-15T11:15:00+00:00`
- Provider: `openai_compatible` (live LLM), embedding: `fake`
- Live benchmark: `4/4` repositories passed the benchmark checks
- Trend: `pass`, 4 repositories newly evaluated
- Release rehearsal: `warning` because hosted delivery remains operator-guided

| Profile | Repository | Import | Sparse status | Normal attempts | Created | Sparse attempts | Recovered | Elapsed seconds |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| small_sparse | drisspg/transformer_nuggets | succeeded | exhausted | 3 | 0 | 1 | 0 | 26 |
| docs_heavy | harbor-framework/terminal-bench-science | succeeded | skipped | 43 | 29 | 0 | 0 | 690 |
| medium_decision_rich | sirkirby/unifi-mcp | succeeded | skipped | 74 | 51 | 0 | 0 | 772 |
| stress | LiPu-jpg/Openwrite | succeeded | skipped | 0 | 0 | 0 | 0 | 0 |

## Interpretation

- `small_sparse` exercised sparse recovery and ended `exhausted` after a live model attempt with `null_decision` rejection.
- `docs_heavy` and `medium_decision_rich` produced normal candidates and therefore recorded sparse recovery as `skipped/candidate_present`.
- `stress` imported successfully but had no eligible evidence, so the result remains `evidence_limited` rather than being promoted to a pass.
- Hosted URLs and recovery remain `operator_guided`; this is an honest local-stack rehearsal, not an externally hosted deployment claim.

## Security Boundary

Bounded repository ids, workspace slugs, statuses, counters, provider mode, and rejection categories only; no tokens, raw model output, or source content.
