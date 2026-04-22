# 2026-03-26 Update Log

## Summary

Today the project crossed an important threshold in the real-repository lane:

- imported-workspace analysis for `n8n-io/n8n` produced real reviewable candidate decisions
- why-search returned grounded answers against accepted imported decisions
- drift evaluation produced real alerts instead of staying in an unevaluated state
- the extraction-throughput change was archived and synced to main specs
- the local PostgreSQL-backed real stack now has one-command start and stop scripts

The highest-signal takeaway is that the product is no longer just able to import a real public repository. It can now turn that repository into:

- candidate decisions
- accepted decisions
- why answers
- drift alerts

with an end-to-end local workflow that is easier to operate repeatedly.

## Delivered Today

### 1. Real repository validation produced reviewable candidates

Validated the imported workspace flow against `n8n-io/n8n`.

Observed imported-workspace output:

- imported artifacts: `1158+`
- high-signal repository documents: `39`
- extraction shortlist: `80`
- full extraction attempts: `37`
- generated candidate decisions: `27`

This is the most meaningful product change from a validation perspective:

- previous real-repository runs often ended with `screened-in -> 0 candidate`
- current runs now produce a meaningful review queue

### 2. Why-search and drift were validated against real imported decisions

Validated downstream behavior after accepting imported candidates.

Current state:

- why-search now returns citation-backed answers against imported accepted decisions
- drift evaluation can be run manually and now produces visible alerts such as:
  - `possible_supersession`
  - `needs_review`

The real lane is still imperfect:

- why-search can still over-merge adjacent accepted decisions into one answer
- drift alert precision is still conservative and somewhat noisy

But the core chain is now functioning:

```text
real import
  -> candidate decisions
  -> accepted decisions
  -> why answers
  -> drift alerts
```

### 3. One-command real-stack startup and shutdown

Added a managed PostgreSQL-backed local real stack workflow.

New scripts:

- [start-real-stack.ps1](../../scripts/dev/start-real-stack.ps1)
- [stop-real-stack.ps1](../../scripts/dev/stop-real-stack.ps1)
- [start-real-stack.bat](../../scripts/dev/start-real-stack.bat)
- [stop-real-stack.bat](../../scripts/dev/stop-real-stack.bat)

New package commands:

- `pnpm run dev:real`
- `pnpm run dev:real:stop`

What the real-stack startup does:

- starts Docker `postgres` and `redis`
- runs engine migrations against PostgreSQL
- seeds `demo-workspace` into PostgreSQL
- starts `engine`, `api`, and `web`
- records managed process state in `.tmp/real-stack.json`

What the shutdown flow now does:

- stops managed services by recorded PID when state exists
- falls back to port-based shutdown for `3000/3001/8000` when state is missing
- stops Docker `postgres` and `redis`

### 4. OpenSpec closure for extraction throughput

Archived:

- `openspec/changes/archive/2026-03-26-improve-decision-extraction-throughput/`

Synced main specs:

- [decision-extraction-throughput/spec.md](../../openspec/specs/decision-extraction-throughput/spec.md)
- [live-repository-analysis/spec.md](../../openspec/specs/live-repository-analysis/spec.md)

At this point, the throughput change is no longer active and its spec updates are part of mainline OpenSpec.

### 5. README real-stack workflow update

Updated [README.md](../../README.md) to reflect the current operating model:

- how to start and stop the PostgreSQL-backed real stack
- what the real stack script actually does
- current live-analysis boundaries
- current known limitations in:
  - extraction
  - why-search
  - drift
  - indexing

## Commits Added Today

- `1da2644` `feat: archive extraction throughput changes`
- `ff54c6b` `docs: update readme for real stack workflow`

## Verification

Verified during today’s work:

- managed real-stack startup returns healthy endpoints:
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:3001/health`
  - `http://127.0.0.1:3000`
- managed real-stack shutdown now clears app services and stops Docker `postgres` / `redis`
- real imported workspace for `n8n-io/n8n` now produces:
  - reviewable candidate decisions
  - why-answer output
  - drift alerts

## Current Project State

The project is now best described as:

- guided demo lane stable
- real repository lane meaningfully functional
- local real-stack operation simplified
- throughput and conversion changes archived into OpenSpec mainline

The main question is no longer:

- "Can the product do real repository analysis at all?"

The main question is now:

- "How much can we improve quality, precision, and focus in the real lane?"

## Recommended Next Step

The next sensible improvement should be quality-focused rather than throughput-focused.

Best candidates:

1. improve extraction conversion quality further
   - better quote grounding
   - better artifact-family prompts
   - better salvage precision
2. improve why-search focus
   - reduce multi-decision answer blending
   - tighten top-hit selection
3. improve drift precision
   - reduce alert overreach
   - better separate true supersession from related follow-up work
