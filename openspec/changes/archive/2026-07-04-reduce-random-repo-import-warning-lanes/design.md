## Context

The project now has multiple release-readiness evidence collectors: multi-repo live diagnosis, one-command release rehearsal, full-chain random repo release rehearsal, customer-host evidence, and external-host trial evidence. These collectors correctly preserve warning/operator-guided states, but the resulting release bundle does not yet explain which warnings are product-controlled versus external, manual, or missing-input noise.

This change adds a small aggregation layer that reads existing JSON outputs and produces an actionable warning-lane reduction report. It is intentionally evidence-only: it does not rerun imports, change release gates, or rewrite source collector statuses.

## Goals / Non-Goals

**Goals:**
- Classify source warning lanes into stable, release-readable categories.
- Preserve source status and evidence paths so the report is auditable.
- Emit JSON and Markdown that can be archived with release readiness evidence.
- Provide priority-ordered follow-up actions for product work and operator disclosure.

**Non-Goals:**
- Do not downgrade warning/operator-guided lanes to pass.
- Do not require network, browser, model, GitHub, or local stack access.
- Do not replace existing release rehearsal, full-chain, benchmark, or readiness-history collectors.
- Do not inspect private repository contents or raw logs.

## Decisions

1. Add a standalone `collect_random_repo_warning_lane_reduction.py` script.
   - Rationale: Existing collectors already generate bounded evidence; a standalone reducer avoids coupling release execution to classification logic.
   - Alternative considered: add classification directly into full-chain release rehearsal. Rejected because it would make the full-chain collector larger and harder to test independently.

2. Use deterministic keyword and status-based classification.
   - Rationale: Release evidence must be reproducible and safe to run offline.
   - Alternative considered: use an LLM to summarize warnings. Rejected because it adds cost, provider dependency, and nondeterminism to release gates.

3. Treat source evidence as immutable.
   - Rationale: The reducer explains warning lanes but must not hide the upstream truth.
   - Alternative considered: compute a cleaner top-level status after classification. Rejected because it can make incomplete evidence look release-clean.

4. Emit both machine and operator formats.
   - Rationale: JSON supports trend/history integration; Markdown is the human handoff artifact.
   - Alternative considered: JSON only. Rejected because release rehearsal already produces human-readable evidence.

## Risks / Trade-offs

- Keyword classification may be imperfect -> keep source lane IDs/statuses and expose category rationale so misclassification is reviewable.
- Evidence schemas can drift -> parse defensively and mark unknown/missing sources as `not_provided` rather than crashing.
- The report may add another warning artifact -> make the value explicit through prioritized reduction actions and category counts.
- It does not reduce warnings by itself -> document that it is a triage layer; actual product fixes remain separate changes.

## Migration Plan

Add the reducer and tests without changing existing release gate behavior. Generate a smoke report from current `.tmp` evidence. Later changes can wire the reducer into one-command release rehearsal or readiness-history archival if the output proves useful.
