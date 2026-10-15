## Context

Real-repo evidence now identifies why/drift warnings as `missing_accepted_decision_evidence`, but it does not expose a baseline status that operators can track over releases. For `Textualize/rich`, the review queue can contain candidates while the accepted-decision baseline remains empty, which makes why answers and drift follow-up difficult to ground.

## Goals / Non-Goals

**Goals:**

- Add an accepted-decision baseline summary to imported workspace core-loop reports.
- Reuse existing decision list APIs and bounded evidence fields.
- Propagate baseline status through multi-repo diagnosis and warning-lane reduction.
- Keep candidate review and accepted baseline separate so the system does not pretend human review happened.

**Non-Goals:**

- Do not auto-accept imported candidate decisions.
- Do not add database migrations, new endpoints, or a new UI flow in this change.
- Do not call paid model providers in deterministic tests.
- Do not embed raw private source, raw model output, or secrets in evidence.

## Decisions

1. Probe accepted decisions through the existing `/decisions` API.

   Rationale: The collector already probes candidate decisions. Querying `review_state=accepted` gives a bounded baseline signal without adding API surface.

   Alternative considered: infer accepted count from dashboard summary only. Rejected because the dashboard count does not provide sample titles or a dedicated baseline status.

2. Add `accepted_baseline` as compact metadata, not a new lane.

   Rationale: The baseline explains `why_search` and `drift` quality. Making it a separate top-level lane would change existing pass/warning rollups and make trend history harder to compare.

   Alternative considered: fail the review lane when accepted count is zero. Rejected because an empty accepted baseline is a quality explanation, not always a review API failure.

3. Feed baseline status into grounding reason evidence.

   Rationale: `missing_accepted_decision_evidence` should show whether the baseline is empty, thin, or unavailable so the next remediation is clear.

   Alternative considered: keep the reason code only. Rejected because release evidence would still require manual lower-level inspection.

## Risks / Trade-offs

- Accepted decisions may be intentionally empty during early import -> Keep status as `empty`/`thin` metadata instead of turning the whole run blocking.
- Extra API probe can fail independently -> Classify unavailable baseline as warning metadata and preserve existing lane statuses.
- Sample titles can leak too much context -> Bound samples to a small list of titles only and avoid raw source excerpts.
