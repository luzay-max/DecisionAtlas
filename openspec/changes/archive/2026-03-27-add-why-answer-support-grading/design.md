## Context

Imported why-search is now focused enough to pick the right primary decision for many real-repository questions, but the result model still has a hard cliff between `ok` and `insufficient_evidence`. In real validation, some answers clearly hit the right accepted decision and expose one strong source reference, yet the product labels them as if the system failed to answer at all.

The current trust boundary is still correct and should be preserved:

- imported why-search must remain grounded in accepted decisions
- citations must remain the reason an answer is considered trustworthy
- the change should not loosen into free-form or speculative answering

This change is cross-cutting because it touches engine result classification, API payloads, and web rendering/state messaging. It is also a product semantics change: the system needs to say "this answer is partially supported" instead of incorrectly collapsing it into "no usable answer."

## Goals / Non-Goals

**Goals:**

- Introduce a graded imported why-answer state for partially grounded answers.
- Distinguish `limited_support` from true `insufficient_evidence`.
- Keep the existing accepted-decision trust boundary and fail-closed path for genuinely weak matches.
- Expose the new support grade clearly in API and UI surfaces.
- Add regression coverage for one-citation imported why cases.

**Non-Goals:**

- Increase source-ref coverage or extraction grounding quality in this change.
- Rework why retrieval or primary-hit selection beyond what is needed to classify support strength.
- Replace citation-based trust with a softer qualitative heuristic.
- Change drift, extraction throughput, or workspace reuse behavior.

## Decisions

### Decision: Grade support after primary decision selection, not before retrieval

The system will keep the current focused why-search flow:

```text
question
  -> query rewrite
  -> accepted decision retrieval
  -> primary decision selection
  -> citation/support evaluation
  -> status classification
```

Why:

- the current issue is not retrieval ambiguity in the tested case
- support grading should describe the confidence of the selected answer, not change the retrieval contract

Alternatives considered:

- grade support during retrieval scoring
  - rejected because retrieval and evidence sufficiency are separate concerns
- treat one-citation answers as fully `ok`
  - rejected because that would overstate trustworthiness

### Decision: Add `limited_support` as a first-class why outcome

Imported why-search will classify partially grounded answers into a distinct status when:

- a primary accepted decision is selected
- the answer is still directionally correct and citation-backed
- but the current support is below the full `ok` threshold

Why:

- this preserves conservative trust while avoiding false-negative messaging
- it tells the truth about what the system knows today

Alternatives considered:

- keep using only `insufficient_evidence`
  - rejected because it conflates "wrong or missing answer" with "correct but thinly supported answer"
- lower the `ok` threshold instead
  - rejected because it weakens the meaning of a fully supported answer

### Decision: Keep `ok` stricter than `limited_support`

The meaning of `ok` will remain stronger than the new partial-support state.

Why:

- users need a clear distinction between strong grounding and partial grounding
- preserving a stricter `ok` state avoids quietly weakening product claims

Alternatives considered:

- merge `ok` and `limited_support` into one success bucket with inline copy
  - rejected because downstream UI and evaluation become less explicit

### Decision: Represent limited support explicitly in the API payload

The response contract will carry the new status in the same result shape used by why-search today, rather than hiding it inside UI-only derived state.

Why:

- API consumers and tests need access to the distinction
- the frontend should not infer support grading indirectly from citation counts

Alternatives considered:

- compute limited support only in the frontend
  - rejected because support grading is a backend trust decision, not a presentation guess

## Risks / Trade-offs

- **[Risk] `limited_support` becomes an excuse for weak answers** → Mitigation: require a primary accepted decision and at least one citation-backed source before using it.
- **[Risk] status proliferation makes why behavior harder to understand** → Mitigation: keep the new state narrowly defined and message it distinctly from `ok` and `insufficient_evidence`.
- **[Risk] users over-trust partial answers anyway** → Mitigation: keep copy explicit that the answer is useful but not yet fully supported.
- **[Risk] future source-ref coverage work changes the threshold assumptions** → Mitigation: define the status around relative support strength, not around a hard-coded UI-only interpretation.

## Migration Plan

1. Add backend classification for partially grounded imported why-answers.
2. Extend why API responses and frontend status handling to surface `limited_support`.
3. Update imported why UI copy to explain the new state and recommended next step.
4. Add regression tests for one-citation imported why answers and preserve existing `ok` / `insufficient_evidence` behavior.

Rollback is straightforward:

- remove the new status and revert to the prior `insufficient_evidence` path
- no database migration or stored-data migration is required

## Open Questions

- Should `limited_support` be limited to imported workspaces only, or should demo-mode answers eventually use the same grading model?
- Should the next-action hint for `limited_support` point users toward reviewing more candidates, re-running analysis, or inspecting decision detail/source refs first?
- Should the support-grading rules eventually become benchmark-driven rather than citation-count-driven once source-ref coverage improves?
