## Context

The self-hosted team workflow rehearsal proved that browser-level account and role boundaries work, but the optional live benchmark lane still produced `missing_workspace` for `fastapi/fastapi`. That is an honest outcome, but it is not enough to claim a real public repository has been validated.

Existing benchmark tooling can select curated public repositories and report missing workspaces. Existing import APIs and readiness summaries can represent imported workspaces. The gap is the rehearsal bridge: an operator needs one repeatable command path that imports or reuses the selected public GitHub repository before running the benchmark comparison.

## Goals / Non-Goals

**Goals:**

- Provide a repeatable public GitHub rehearsal path for `fastapi/fastapi`.
- Reuse existing live-analysis/import APIs instead of introducing a new import backend.
- Keep missing workspace, import failure, and benchmark product limitations distinct in generated evidence.
- Produce `.tmp` JSON/Markdown evidence that can later be archived into readiness history.
- Update documentation so release claims do not treat selected-but-not-imported repositories as benchmark passes.

**Non-Goals:**

- Do not implement the full multi-provider Git source plan in this change.
- Do not add private token paste, GitLab, Gitee, local-path import, or credential storage.
- Do not make live public GitHub import part of default CI.
- Do not require network access for offline validation.

## Decisions

1. Use a narrow rehearsal command instead of extending the default release gate.
   - Rationale: live GitHub access and a running local stack are operator-guided conditions; making them default CI requirements would make validation flaky.
   - Alternative considered: make `run_benchmark.py --live-real-repos` auto-import missing workspaces. Rejected because the benchmark runner should measure imported workspaces and not silently mutate application state.

2. Import or reuse happens before benchmark validation.
   - Rationale: the current failure was not benchmark quality; it was missing setup. Separating setup from measurement keeps evidence honest.
   - Alternative considered: classify `missing_workspace` as warning and continue. Rejected because it still leaves no proof that the real repository can be analyzed.

3. Start with public GitHub only.
   - Rationale: public GitHub import exercises the real-repo path without introducing private credential risk. Multi-provider token import remains the next larger P1 change.
   - Alternative considered: implement GitHub/GitLab/Gitee/token support together. Rejected because it mixes rehearsal reliability with credential/product surface design.

4. Evidence remains scratch by default.
   - Rationale: `.tmp` outputs are local proof. Durable release claims must explicitly archive selected artifacts with readiness history.
   - Alternative considered: commit generated live outputs. Rejected because they can become stale and may include local environment details.

## Risks / Trade-offs

- [GitHub/network unavailable] -> The rehearsal records `operator_guided` or provider failure and does not claim pass.
- [Repository imports but produces weak candidates] -> Benchmark evidence must classify product limitation separately from setup success.
- [Local stack state is stale] -> Rehearsal should create or reuse the expected workspace and report the chosen path.
- [Public import grows into credential handling] -> Keep this change scoped to public GitHub; private token work belongs to `multi-git-source-token-import`.
