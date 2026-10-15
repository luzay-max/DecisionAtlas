## Context

Existing scripts cover public GitHub import setup and real-repo benchmark trends. Existing browser tests cover demo workspace and mocked repository UI flow. The missing slice is a single evidence artifact that proves or honestly classifies whether an imported workspace can move through the core product loop: dashboard, review, why-search, drift, and governance guardrail.

The collector should be safe to run locally and in CI. It should not require a private token. It should be able to consume a previously generated public import rehearsal JSON, because import may be created/reused by another step.

## Goals / Non-Goals

**Goals:**

- Produce JSON and Markdown evidence for imported workspace core-loop readiness.
- Use real public GitHub repository identity from input or public import rehearsal output.
- Probe existing local API endpoints without mutating repository contents.
- Keep limitations explicit: not provided, operator guided, local stack failure, provider failure, and warning.
- Add deterministic tests and a browser rehearsal with mocked API responses.

**Non-Goals:**

- Do not force a live GitHub import in every test run.
- Do not require private repo credentials.
- Do not replace real-repo benchmark comparison.
- Do not make guardrail advisory output a hard correctness proof.

## Decisions

1. Build a collector script rather than embedding this in release evidence.
   - Rationale: this lane should be reusable before it becomes part of one-command release rehearsal.
   - Alternative: directly extend release evidence. Rejected because this slice should be independently testable first.

2. Accept import rehearsal JSON as an optional source.
   - Rationale: import/reuse is already implemented and tested; core-loop rehearsal should compose with it.
   - Alternative: duplicate import logic. Rejected to avoid inconsistent setup classification.

3. Treat browser rehearsal as UI-flow proof, not live import proof.
   - Rationale: deterministic browser tests should not depend on GitHub availability, but they must preserve the real repository reference and evidence boundary.

## Risks / Trade-offs

- Live local stack may be unavailable. Mitigation: classify as `local_stack_failure` and still emit evidence.
- A workspace may have no candidates or accepted decisions. Mitigation: mark review/why lane as warning or operator-guided rather than pass.
- Guardrail is project-level, not workspace-specific. Mitigation: record it as governance lane and explicitly avoid treating it as correctness proof.
