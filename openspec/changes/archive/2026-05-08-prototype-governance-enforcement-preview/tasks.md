## 1. Guardrail Preview Model

- [x] 1.1 Add an enforcement preview data shape derived from `AgentGuardrailResult` without changing the existing `continue`, `caution`, and `pause` status model.
- [x] 1.2 Implement preview mapping so `pause`, blocked diff checks, and review-required drift set `would_block: true`.
- [x] 1.3 Implement preview mapping so `caution` produces warning evidence but remains non-blocking.
- [x] 1.4 Preserve source evidence, human questions, recommended actions, and advisory/default metadata in preview output.
- [x] 1.5 Add a source-linked override prompt or handoff field for would-block false-positive review.

## 2. CLI and Report Output

- [x] 2.1 Add explicit opt-in CLI options for enforcement preview mode while preserving default command behavior and exit code.
- [x] 2.2 Add optional local strict exit behavior that returns non-zero only when opt-in preview output has `would_block: true`.
- [x] 2.3 Add report-oriented output suitable for PR annotation text without calling GitHub or requiring network access.
- [x] 2.4 Add release checklist warning output or summary text that can be copied into readiness records without modifying release gates.

## 3. Documentation

- [x] 3.1 Update guardrail documentation with opt-in preview modes, default advisory semantics, and strict-exit behavior.
- [x] 3.2 Document the false-positive override handoff and make clear that overrides are human-authored.
- [x] 3.3 Update release checklist or hosted-preview readiness guidance to record optional preview evidence without treating it as default CI enforcement.

## 4. Validation

- [x] 4.1 Add tests proving the default guardrail JSON and summary commands still return success for advisory `pause`.
- [x] 4.2 Add tests for preview mapping across `continue`, `caution`, and `pause`.
- [x] 4.3 Add tests for strict exit behavior only failing on `would_block: true`.
- [x] 4.4 Add tests that PR annotation or report output preserves source evidence and does not require remote provider access.
- [x] 4.5 Run targeted governance guardrail tests and `openspec validate prototype-governance-enforcement-preview --strict`.
