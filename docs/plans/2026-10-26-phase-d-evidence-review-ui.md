# Phase D — evidence review UI and interaction

Base: Phase C merge f7e64346874d4a1d6ff0eef82f876df2995b8d6e; post-merge CI #242 passed. This phase adds a read-only evidence presentation layer using fields the web API already returns. It does not connect the Phase-C offline review packet to a new API or claim the public capture verifier has run for these live UI records.

## Scope in this PR

1. Replace the raw source-reference list on decision details with a responsive evidence panel.
2. Display quote availability, safe HTTP(S) source-link availability, and whether a nonnegative source span is recorded. These are metadata completeness checks only, not semantic support or source authenticity.
3. Add a compact evidence boundary notice to the review queue so reviewers know imported quotes and URLs have not been independently verified by this UI.
4. Add EN/ZH copy, accessible labels, safe external links, and tests for complete/missing metadata, invalid URLs, empty sources, and compact queue mode.
5. Keep existing explicit Accept/Reject/Supersede actions unchanged. No new review-state mutation, database field, backend route, network fetch, or authentication change.

## Non-goals and acceptance gates

- This UI does not verify current upstream GitHub content, whether a proposal was merged/adopted, or whether a quote semantically supports the decision.
- It does not persist independent human annotation, authenticate reviewers, or modify the Phase-C offline submission workflow.
- No private evidence export or user-specific artifact is committed.
- CI must pass on the final PR head in Windows GitHub Actions, including web typecheck, component tests, E2E/browser smoke tests, and the full engine suite.
- Human review remains not_run until actual independent reviewers complete a separately controlled process.


## Synthetic imported-style UI visual acceptance (2026-10-26)

The Playwright smoke seed now creates a separate **CI-only synthetic** workspace,
`ci-evidence-preview`, inside the ephemeral .tmp/smoke.db database. Its title
and content explicitly identify it as a fictional preview, not a real GitHub
import or proof of adoption. The fixture has one complete source reference and
one incomplete reference, to show both available and missing metadata in the UI.

A new Playwright flow visits the imported-workspace review queue and decision
detail using the real web and API route, checks source metrics and the
independent-review limitation, verifies no sideways overflow at mobile width,
and saves four desktop/mobile screenshots to CI's existing public-demo-artifact
collection. No review-state mutation, private repository data or live importer
credentials are involved.

Review screenshot artifacts separately from real model/accuracy claims; these
are UI appearance tests only.


### Source labeling correction

The CI-only fixture now uses `seed-` prefixed artifact IDs, so the
existing provenance resolver correctly labels it as demo/synthetic data. The
review page also prefers `workspace_mode` and `source_summary` from
its actual API response over inferring authenticity from the workspace slug.
This avoids falsely describing fictional CI screenshots as actual GitHub imports.
