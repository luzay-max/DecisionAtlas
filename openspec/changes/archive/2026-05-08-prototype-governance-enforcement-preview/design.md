## Context

The current governance agent guardrail aggregates the governance diff checker and drift detector into `continue`, `caution`, or `pause`. Its CLI returns success by default for every advisory result, including `pause`, and the documentation repeatedly states that guardrail output is not default CI enforcement.

Stage 13 should make the next step visible without changing that contract. The useful product move is an opt-in preview layer that answers: "If stricter governance were enabled here, would this result block, warn, or pass?" The answer must remain traceable to the same source evidence already present in the guardrail result.

## Goals / Non-Goals

**Goals:**

- Add opt-in enforcement preview semantics for local agent workflows.
- Preserve the existing default advisory CLI behavior and default release gate behavior.
- Strongly flag only `pause`, blocked diff checks, and review-required drift.
- Keep `caution` as a warning that must be disclosed or addressed, not as a blocker.
- Produce machine-readable preview output that can be reused in local summaries, PR annotation text, and release checklist warnings.
- Preserve source evidence, human questions, recommended actions, and an explicit advisory/default marker.
- Define a lightweight false-positive override handoff that records the human decision without mutating project files automatically.

**Non-Goals:**

- No default CI blocking.
- No GitHub API integration or live PR commenting in this first slice.
- No database-backed override audit log.
- No automatic code, OpenSpec, roadmap, documentation, or accepted-rule rewrites.
- No changes to the underlying diff checker or drift detector classification logic unless required for wiring.

## Decisions

1. Add preview semantics as an outer layer around the existing guardrail result.

   The current aggregator already has the right conservative source status. The preview layer should derive fields such as `mode`, `would_block`, `severity`, `block_reasons`, `warning_reasons`, `override_required`, and `source_evidence` from the existing result rather than re-running or reinterpreting diff/drift logic. This keeps the change small and avoids changing the advisory status taxonomy.

   Alternative considered: add enforcement status directly into the diff checker and drift detector. Rejected because those tools are still advisory sources and should not each learn downstream workflow policy.

2. Keep default CLI behavior unchanged.

   Running `python scripts/governance/agent_guardrail.py --summary` or the default JSON command must still return exit code `0` for `continue`, `caution`, and `pause`. Opt-in behavior should require an explicit flag. A local strict exit option may return non-zero only when the derived preview says `would_block: true`.

   Alternative considered: make `pause` return non-zero by default. Rejected because it would violate the current specs, hosted preview docs, and release baseline separation.

3. Treat PR annotation mode as generated report text, not a GitHub integration.

   The first slice can emit Markdown or JSON fields suitable for a PR comment or annotation. It should not call `gh`, GitHub APIs, or depend on remote authentication. This keeps the preview deterministic and locally testable.

   Alternative considered: post comments directly to GitHub. Rejected because network/auth failures would add operational risk and make the feature harder to validate locally.

4. Record false-positive override as handoff data first.

   The preview should expose what human decision is needed to override a false positive and how to cite the evidence. The first slice should document and emit a reusable override note or prompt, not persist override decisions in the database.

   Alternative considered: add durable override storage. Rejected for this stage because it requires data model, permissions, and audit semantics that are larger than a preview.

5. Keep release checklist integration warning-only.

   Release checklist mode should help operators record the latest preview result as readiness evidence. It must not add guardrail enforcement to the default `pre-release.ps1` or other mandatory local release commands.

## Risks / Trade-offs

- [Risk] Users misread "enforcement preview" as production CI enforcement. -> Mitigation: every output mode includes explicit default-advisory wording and docs repeat that default release gates are unchanged.
- [Risk] A `caution` result becomes over-strict and blocks useful work. -> Mitigation: only `pause`, blocked diff, or review-required drift can set `would_block: true`.
- [Risk] Preview output duplicates existing handoff fields and becomes inconsistent. -> Mitigation: derive preview fields from the existing `AgentGuardrailResult` in one helper and test the mappings.
- [Risk] PR annotation scope expands into remote GitHub integration. -> Mitigation: limit this change to report generation suitable for annotations; leave posting to a future change.
- [Risk] False positive overrides lack durable auditability. -> Mitigation: make the override handoff explicit and source-linked now; defer persistence until override workflows are better understood.

## Migration Plan

- Add the preview helper and CLI flags behind opt-in behavior.
- Add tests proving default JSON and summary commands still return success.
- Add tests for preview mapping across `continue`, `caution`, and `pause`.
- Update guardrail and release docs.
- Rollback is straightforward: remove the opt-in preview flags and helper while keeping the existing guardrail behavior intact.

## Open Questions

- Should the first implementation expose one flag with modes, such as `--enforcement-preview local-strict`, or separate flags such as `--enforcement-preview` and `--strict-exit`?
- Should generated PR annotation text be printed inline, included only in JSON, or optionally written to a local report file?
