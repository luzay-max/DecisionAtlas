## Why

The advisory governance guardrail is now stable enough to explore stricter agent workflow signals, but turning it into a default CI blocker would amplify false positives before the rule quality loop is mature. This change introduces an opt-in enforcement preview that lets operators and agents see what would be blocked while keeping the normal development and release flow advisory by default.

## What Changes

- Add an explicit opt-in governance enforcement preview layer on top of the existing agent guardrail result.
- Provide local strict preview semantics that strongly flag `pause`, blocked diff checks, and review-required drift without changing the default CLI exit behavior.
- Provide report-oriented output suitable for PR annotations or release checklist warnings without requiring GitHub API integration in the first slice.
- Preserve source evidence, human questions, recommended actions, and advisory/default semantics in every preview result.
- Document how a human can override a false positive in the handoff without automatically rewriting code, specs, roadmap documents, or accepted rules.
- No breaking changes: existing guardrail commands remain advisory and exit successfully by default.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ai-agent-governance-guardrails`: add opt-in enforcement preview behavior while preserving default advisory guardrail semantics and source evidence traceability.
- `release-baseline-validation`: clarify that optional enforcement preview warnings can be recorded as readiness evidence but must not become part of the default release gate.

## Impact

- `services/engine/app/governance/agent_guardrail.py`: likely adds preview-mode result fields and CLI options around the existing aggregate result.
- `scripts/governance/agent_guardrail.py`: continues delegating to the engine guardrail CLI.
- `services/engine/tests/governance/test_agent_guardrail.py`: adds regression coverage for default advisory behavior and opt-in preview behavior.
- `docs/project/governance-agent-guardrail.md` and release checklist/readiness docs: document opt-in modes, override handoff, and non-default enforcement boundaries.
- OpenSpec specs: update guardrail and release baseline requirements for explicit opt-in preview semantics.
