## Context

Existing evidence lanes:

- `rehearse_public_github_import.py` checks whether a public repository workspace can be created or reused.
- `collect_imported_workspace_core_loop.py` probes dashboard, review, why-search, drift, and guardrail lanes for one workspace.
- benchmark trend scripts compare metric snapshots but do not orchestrate live diagnosis rotation.

This change composes those existing lanes into a multi-repo operator rehearsal.

## Goals / Non-Goals

**Goals:**

- Select multiple repositories from `examples/live-benchmarks/trend-pool.json` or explicit repo IDs.
- Run setup/core-loop diagnosis per repository.
- Support deterministic random selection so CI and local evidence can be repeated.
- Output compact customer-safe JSON/Markdown.
- Preserve partial/failure states instead of turning a mixed run into pass.

**Non-Goals:**

- Do not add new GitHub import behavior.
- Do not require every repository to import successfully.
- Do not require private credentials.
- Do not replace benchmark comparison or readiness history.

## Decisions

1. Compose existing scripts in-process.
   - Rationale: reuse tested import/core-loop logic without shelling out repeatedly.
   - Alternative: run subprocess commands per repo. Rejected for tests and structured error handling.

2. Use status aggregation at repository and run level.
   - Rationale: one repo can be warning while another is pass; the top-level evidence must disclose this.

3. Keep random selection deterministic.
   - Rationale: the user asked for random real GitHub repos, but release evidence must be reproducible.

## Risks / Trade-offs

- Live stack or GitHub may fail. Mitigation: classify as `local_stack_failure` or `provider_failure`.
- Multiple imports can take time. Mitigation: support no-wait setup and explicit repo selection.
- Some real repos produce weak decision evidence. Mitigation: preserve warning states and feed results into the next quality improvements.
