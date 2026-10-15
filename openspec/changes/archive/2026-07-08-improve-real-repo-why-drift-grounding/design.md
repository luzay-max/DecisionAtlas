## Context

The current real-repo evidence pipeline can identify that `Textualize/rich` still has product-controlled `why_search` and `drift` warnings, but the warning-lane reduction output only says product work remains. That is too coarse for the next release loop because the operator cannot tell whether the issue is missing accepted decisions, weak why-answer support, unresolved drift alerts, or insufficient evidence formatting.

The implementation should stay in the bounded evidence collectors. It should not store raw private source, raw model output, credentials, or large logs.

## Goals / Non-Goals

**Goals:**

- Add compact reason codes for `why_search` and `drift` lanes.
- Preserve product-controlled classification while making each warning actionable.
- Expose reason details in JSON and Markdown evidence consumed by release rehearsal and warning-lane reduction.
- Cover the behavior with unit tests and a real rehearsal run.

**Non-Goals:**

- Do not change database schemas, authentication, team permissions, or UI routing.
- Do not call paid model providers as part of the deterministic CI tests.
- Do not mark weak or missing grounding as pass just to reduce warning counts.
- Do not embed raw repository content or secrets in evidence files.

## Decisions

1. Add reason metadata beside existing lane statuses.

   Rationale: Current consumers already read lane status maps and action-category counts. Adding `lane_reasons` and `grounding_summary` keeps backward compatibility while making warnings explainable.

   Alternative considered: split `why_search` and `drift` into many new lanes. Rejected because it would churn release dashboards and make trend comparison harder.

2. Use bounded reason codes, not free-form raw diagnostics.

   Rationale: Release evidence needs stable comparisons over time. Codes such as `weak_why_support`, `missing_accepted_decision_evidence`, and `unresolved_drift_followup` are easier to test and aggregate than paragraphs.

   Alternative considered: preserve complete raw diagnostics. Rejected because this project must avoid leaking private source, provider output, and noisy logs into artifacts.

3. Let warning-lane reduction surface the reason details for product-controlled lanes.

   Rationale: The reducer is the release-facing summary. It should not force operators to inspect lower-level JSON to understand why a repo is still warning.

   Alternative considered: only update `.tmp/multi-repo-live-diagnosis.json`. Rejected because the final release view would still be too vague.

## Risks / Trade-offs

- Reason codes can become stale if upstream lane names change -> Keep tests on the collector outputs and default to `unknown_grounding_gap` instead of dropping metadata.
- More fields increase JSON size -> Store only compact counts/codes/excerpts, not raw source or model output.
- A warning can look more acceptable once explained -> Keep status semantics unchanged; explanation does not downgrade product-controlled warnings to pass.
