## Context

Current benchmark tooling already provides the building blocks:

- `run_benchmark.py --live-real-repos` creates a current report from existing local imported workspaces.
- `run_benchmark.py --benchmark-snapshot-source` creates a compact snapshot.
- `run_benchmark.py --benchmark-compare-current/--benchmark-compare-baseline` creates comparison JSON/Markdown.
- `collect_real_repo_benchmark_trend.py` turns comparison evidence plus the fixed pool into release-readable trend evidence.

The missing part is an operator-safe wrapper that consistently runs or reuses these steps and records the artifact paths and statuses in one rehearsal summary.

## Goals / Non-Goals

**Goals:**

- Provide one command for fixed-pool benchmark coverage rehearsal.
- Allow offline deterministic tests using supplied fixture reports and snapshots.
- Preserve live mode as explicit/operator-guided.
- Make missing coverage and non-clean trend status visible in the top-level rehearsal summary.
- Keep generated evidence release-safe and `.tmp`-scoped by default.

**Non-Goals:**

- Do not perform GitHub imports automatically.
- Do not call model providers or GitHub APIs directly.
- Do not require existing imported workspaces in default CI.
- Do not mark warning trend coverage as failure unless an internal script error occurs.

## Decisions

1. Use a new wrapper script instead of expanding `run_benchmark.py`.

   `run_benchmark.py` remains the low-level benchmark command. The new script acts as release orchestration and delegates or imports benchmark functions without changing established CLI behavior.

2. Support both `--current-report-json` and `--live`.

   Offline fixture mode is deterministic and CI-safe. Live mode is explicit and operator-guided for local stacks that already have imported workspaces.

3. Write a top-level rehearsal summary.

   Operators need to see whether all expected artifacts were produced and why the final status is `pass`, `warning`, or `blocking`. The summary links the generated current report, snapshot, comparison, and trend files.

4. Treat trend `warning` as rehearsal `warning`.

   A warning means evidence exists but needs operator attention, such as missing fixed-pool repos. Blocking is reserved for schema errors, missing required inputs, or command execution failures.

## Risks / Trade-offs

- Live mode may return missing workspaces -> preserve as operator-guided evidence and do not hide it.
- Baseline snapshot may not include the full fixed pool -> comparison and trend will expose missing coverage.
- Wrapper can duplicate some path logic -> keep it small and test with pure fixture inputs.
