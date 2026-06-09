## Context

The current repository already has:

- `docs/project/code-decision-audit-template.md` as a manual customer report template.
- `collect_release_evidence.py`, `collect_team_handoff_report.py`, `collect_readiness_evidence_history.py`, and benchmark trend/rehearsal scripts.
- Pilot delivery materials for customer evaluation.

The missing step is a bounded local report builder that turns curated evidence JSON into a customer-readable Code Decision Audit report without copying private source material or secrets.

## Goals / Non-Goals

**Goals:**

- Generate Code Decision Audit JSON and Markdown from explicit source paths.
- Preserve warnings and missing optional evidence instead of making a report look clean.
- Include commercial fit and limitations for Community / Team Self-hosted / Enterprise Self-hosted.
- Produce output suitable for a paid pilot or customer evaluation.
- Keep tests deterministic and offline.

**Non-Goals:**

- Do not inspect private repository contents.
- Do not generate model-written analysis from raw code.
- Do not call GitHub, local API, or provider endpoints.
- Do not replace team handoff or readiness history; summarize them.

## Decisions

1. Build a separate report collector.

   The customer audit report has a different audience from release evidence and handoff reports. Keeping it separate avoids mixing operator-only detail with customer-facing language.

2. Use explicit evidence JSON paths only.

   The report builder must not scan `.tmp` implicitly because that can pick stale or sensitive files. Omitted evidence is recorded as `not_provided`.

3. Summarize, do not embed raw evidence.

   The report should include bounded status, counts, paths, and recommendations. It should not embed raw logs, model output, private repo content, or local-only secrets.

## Risks / Trade-offs

- Report can overstate readiness -> preserve non-clean states and include limitations.
- Evidence may be omitted -> show `not_provided` in JSON/Markdown.
- Customer report may duplicate handoff report -> focus on customer value, commercial fit, and next actions.
