# Accepted Decision Baseline

## Purpose

This change makes real-repository why/drift quality depend on an explicit accepted-decision baseline instead of only reporting missing grounding. It helps operators see whether a repository has enough reviewed decisions to support why answers and drift follow-up.

## Implemented

- Added accepted-decision baseline probing to imported workspace core-loop evidence.
- Added `accepted_baseline` to core-loop JSON and Markdown.
- Included accepted baseline status/counts in why/drift grounding evidence.
- Propagated accepted baseline summaries through multi-repo live diagnosis.
- Included accepted baseline details in random repo warning-lane reduction classified lanes.

## Real Evidence

- Real repositories: `n8n-io/n8n` and `Textualize/rich`.
- `n8n` baseline: `present`, `established`, accepted count `7`.
- `rich` baseline: `empty`, accepted count `0`, candidate count `35`.
- `rich` why/drift warning remains grounded as `missing_accepted_decision_evidence`.

## Boundary

This change does not auto-accept candidate decisions. It preserves the human review boundary and makes the next action explicit: review selected `rich` candidates into an accepted baseline before expecting why/drift lanes to become clean.
