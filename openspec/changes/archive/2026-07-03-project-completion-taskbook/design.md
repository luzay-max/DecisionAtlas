## Context

The 2026-05-08 and 2026-05-09 plans define the target direction: stable development protocol, better governance quality, real repository regression, self-hosted delivery, commercial packaging, and complete user workflow. Since those plans were written, many changes have been implemented and archived, but the plan documents do not provide a current execution ledger.

The taskbook is not a replacement for OpenSpec. It is a navigation layer that tells the operator which OpenSpec changes and evidence prove each product-readiness claim.

## Goals / Non-Goals

**Goals:**

- Create one current taskbook that maps plan goals to evidence and next work.
- Use explicit states: complete, partial, missing, blocked, and not-now.
- Include validation evidence references: archived change names, docs, tests, browser rehearsals, and readiness artifacts.
- Define the next OpenSpec queue without overcommitting to SaaS/billing/multi-tenant work.

**Non-Goals:**

- Do not implement a new task management application.
- Do not replace OpenSpec proposal/design/tasks.
- Do not claim final product completion where evidence is partial.
- Do not introduce billing, Marketplace, or hosted managed service scope.

## Decisions

1. Use Markdown for the taskbook.
   - Rationale: The project already uses Markdown plans, update logs, and OpenSpec files.
   - Alternative: Add a JSON tracker. Rejected for this slice because the operator needs readable planning first.

2. Track evidence quality, not just task completion.
   - Rationale: The goal explicitly requires real tests, browser operation, and real GitHub repository evidence; weak evidence must remain visible.
   - Alternative: Simple checkbox list. Rejected because it hides whether a claim is actually proven.

3. Keep future work as OpenSpec candidates.
   - Rationale: The project workflow depends on proposal -> design/specs -> tasks -> apply -> archive.

## Risks / Trade-offs

- The taskbook can become stale. Mitigation: require update-log and OpenSpec archive references after each change.
- A document-only change can feel less useful than code. Mitigation: this taskbook directly chooses the next implementation queue and prevents repeated or misprioritized work.
- Evidence categories can be too broad. Mitigation: use concrete proof references for each line.
