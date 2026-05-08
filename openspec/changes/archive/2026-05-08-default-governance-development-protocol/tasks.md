## 1. Protocol Status Surface

- [x] 1.1 Inspect existing `scripts/governance/agent_guardrail.py` output fields and tests to identify reusable protocol data.
- [x] 1.2 Add a compact local protocol status entrypoint or guardrail mode that reports active OpenSpec context, guardrail status, diff status, required tests, recommended actions, human questions, and handoff guidance.
- [x] 1.3 Ensure the protocol status is derived from existing guardrail fields rather than duplicating governance decision logic.
- [x] 1.4 Preserve advisory-only behavior so the new protocol status does not mutate files or fail default validation solely because of `caution` or `pause`.

## 2. Tests

- [x] 2.1 Add targeted tests for protocol status output when no active OpenSpec change exists.
- [x] 2.2 Add targeted tests for protocol status output when guardrail status is `continue`.
- [x] 2.3 Add targeted tests for protocol status output when guardrail status is `caution`, including required disclosure or recommended actions.
- [x] 2.4 Add targeted tests for protocol status output when guardrail status is `pause`, including human questions and disallowed self-remediation behavior.

## 3. Documentation

- [x] 3.1 Update `docs/project/governance-agent-guardrail.md` to describe the default local development protocol and checkpoints.
- [x] 3.2 Update README workflow guidance to reference governance preflight, postflight, archive, and commit handoff behavior.
- [x] 3.3 Update `docs/project/release-checklist.md` to record protocol evidence separately from the canonical release gate and optional enforcement preview.
- [x] 3.4 Update Chinese-facing documentation when an English entry point changes.

## 4. Validation

- [x] 4.1 Run targeted governance tests for the new protocol status behavior.
- [x] 4.2 Run `python scripts/governance/agent_guardrail.py --summary` and the new protocol status command or mode.
- [x] 4.3 Run `openspec validate --all --strict`.
- [x] 4.4 Record validation evidence in the implementation handoff.
