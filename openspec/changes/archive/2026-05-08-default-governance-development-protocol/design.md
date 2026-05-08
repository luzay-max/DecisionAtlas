## Context

DecisionAtlas now has governance diff checking, governance drift detection, AI-agent guardrails, governed hosted preview guidance, and release checklist coverage. The 2026-05-08 master plan identifies the next priority as making these capabilities stable defaults for development instead of optional scripts that depend on operator memory.

The existing guardrail already produces `continue`, `caution`, and `pause`, plus workflow protocol fields. The missing layer is a repeatable local development protocol that tells agents and developers when to run checks, how to summarize results, and how to handle caution or pause before claiming completion.

## Goals / Non-Goals

**Goals:**

- Make governance preflight and postflight explicit for non-trivial local changes.
- Provide a compact status entrypoint or mode that combines OpenSpec context, guardrail result, validation expectations, and handoff obligations.
- Document how developers and AI agents use the protocol before implementation, after implementation, before archive, and before commit.
- Preserve advisory-first semantics and make `pause` a human decision signal.
- Keep release documentation clear about the difference between default development protocol, canonical release baseline, and optional enforcement preview.

**Non-Goals:**

- No default CI blocking.
- No automatic code, spec, roadmap, documentation, or accepted-rule rewrites.
- No GitHub PR bot or remote annotation integration.
- No new external provider dependency.
- No replacement for OpenSpec proposals, tasks, validation, or human review.

## Decisions

1. Use the existing guardrail result as the protocol source of truth.

   The current `agent_guardrail.py` already aggregates diff and drift results and emits machine-readable guidance. Reusing it avoids a second governance engine and keeps output semantics consistent. The new work should wrap or extend the existing output rather than reimplementing status logic elsewhere.

2. Add a lightweight status surface instead of a heavy workflow service.

   The protocol needs a local command or mode that agents can run from the repository root. It should summarize active OpenSpec changes, guardrail status, required tests, recommended actions, and handoff text. A local script is enough for this slice; a daemon, UI, or SaaS workflow engine would add unnecessary scope.

3. Treat `pause` as a stop-and-ask protocol step, not enforcement.

   The existing product boundary says guardrails are advisory by default. This change should strengthen the workflow by making pause visible and actionable, but it must not silently mutate files or fail the default release gate.

4. Keep release baseline and development protocol separate.

   The canonical release gate remains `scripts/ci/pre-release.ps1`. The development protocol can be referenced by release documentation and handoffs, but optional enforcement preview and strict exit behavior must stay opt-in.

## Risks / Trade-offs

- Protocol becomes noisy -> Keep the summary compact and focus on status, required validation, recommended actions, and human questions.
- Agents treat advisory output as automatic approval -> Require handoffs to state that `continue` still needs targeted validation.
- Agents treat `pause` as something to self-fix -> Document and test that `pause` asks for human review instead of automatic remediation.
- Duplicate status logic diverges from guardrail output -> Build the protocol status from existing guardrail fields rather than maintaining parallel rules.
- Release docs blur protocol and release gate -> Update release-facing docs to state which checks are default development protocol and which are canonical release validation.
