# Why/Drift Grounding

## Purpose

This change makes real-repository `why_search` and `drift` warnings actionable. Instead of only reporting that `Textualize/rich` still has product-controlled warning lanes, the evidence now preserves compact reason codes and summaries that explain what to fix next.

## Implemented

- Added bounded grounding metadata for product-controlled `why_search` and `drift` warning lanes.
- Added `lane_reasons` and `summary.grounding_summary` to imported workspace core-loop reports.
- Propagated grounding details through multi-repo live diagnosis JSON and Markdown.
- Added grounding details to random repo warning-lane reduction classified lanes and Markdown.
- Updated real guardrail execution to parse the current `agent_guardrail.py --summary` output instead of relying on the removed `--json` flag.

## Current Evidence

- Real stack health passed for Web, API, and Engine.
- Chrome smoke opened `/`, `/evidence`, `/review`, and `/health`.
- Playwright self-hosted team workflow passed.
- Real repositories used: `n8n-io/n8n` and `Textualize/rich`.
- `rich` why/drift warnings now include `missing_accepted_decision_evidence` grounding.

## Boundary

This change does not force warning lanes to pass. It keeps release status honest and makes the remaining warning reasons smaller, stable, and easier to remediate in the next change.
