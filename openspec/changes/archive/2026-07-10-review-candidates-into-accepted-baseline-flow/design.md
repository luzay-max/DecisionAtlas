## Context

The evidence pipeline now reports accepted baseline state. `n8n` has an established baseline, but `rich` remains empty with many candidate decisions. The project needs a repeatable operator flow that can either preview the exact candidates to accept or apply a small accepted baseline mutation with audit rationale.

## Goals / Non-Goals

**Goals:**

- Provide a dry-run-first CLI workflow for accepted baseline promotion.
- Use existing review APIs and audit trail.
- Bound mutation count, rationale size, and output size.
- Produce release-readable JSON/Markdown evidence.

**Non-Goals:**

- Do not auto-review all candidates.
- Do not introduce model-based candidate selection.
- Do not add new database fields or endpoints.
- Do not hide that this is an operator action.

## Decisions

1. Default to dry-run.

   Rationale: Accepting decisions changes the workspace baseline. Operators must opt into mutation with `--confirm-accept`.

   Alternative considered: always mutate during rehearsal. Rejected because it would violate the human review boundary.

2. Select highest-ranked candidates from the existing candidate list order.

   Rationale: The backend already orders candidate decisions by confidence and recency. Reusing that order avoids another ranking algorithm.

   Alternative considered: add source-ref scoring. Rejected for this small change; evidence quality scoring can be a later improvement.

3. Require explicit rationale.

   Rationale: Accepted baseline changes should be auditable and explain why candidates were accepted.

   Alternative considered: use a default rationale silently. Rejected because it would make audit history weaker.

## Risks / Trade-offs

- Operator may accept weak candidates -> Limit count and preserve title/id/rationale evidence for review.
- Live local rehearsal mutates dev data -> Require explicit `--confirm-accept` and bounded `--max-accept`.
- API/auth can reject review -> Preserve error status and before counts instead of reporting success.
