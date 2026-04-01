# 2026-03-27 Next-Phase Roadmap

## Current Position

DecisionAtlas has moved past the "can this work at all?" stage for real imported repositories.

The current baseline is:

- real GitHub repositories can be imported and analyzed
- candidate decisions can be extracted and reviewed
- accepted decisions can power why-search
- why-search now distinguishes `limited_support` from fully supported `ok`
- improved source-ref coverage can upgrade some imported why answers from `limited_support` to `ok`
- drift evaluation is available, but still conservative and somewhat noisy

This means the next phase should focus less on adding brand-new capabilities and more on improving product semantics, operational stability, and repeat-run efficiency.

## Status Update (2026-04-01)

Since this roadmap was written, the first two priorities have already shipped:

- `workspace reuse / incremental sync` is complete
- `GitHub import retry / network resilience` is complete

That changes the forward-looking order to:

```text
1. Drift precision
2. Why-search retrieval quality
3. Indexing modernization for real evidence
```

## Priority 1: Workspace Reuse and Incremental Sync

**Status:** Completed

### Goal

Make repeated analysis of the same repository feel intentional instead of redundant.

### Why This Comes First

Current behavior still tends to treat repeated imports too much like full re-analysis:

- the same repository reuses the same workspace, but this is not surfaced clearly in the product
- users are not guided toward "continue using existing results" vs "run again"
- repeated full runs can waste time and model usage
- old workspace state and new analysis requests are too easy to blur together

### Desired Product Behavior

When a repository already has a workspace:

- offer "continue with existing workspace"
- offer "sync changes since last import"
- offer "run full analysis again" only as an explicit choice

### Scope

- detect existing workspace by repo
- expose workspace reuse more clearly in the UI
- wire `since_last_sync` into the user-facing flow
- avoid defaulting to full reruns when incremental sync is sufficient

### Expected Outcome

- lower repeat-run cost
- clearer product semantics
- better user trust in saved imported workspaces
- less accidental re-analysis

### Completed Outcome

This priority is now implemented:

- existing repositories are looked up before rerun
- the UI exposes `open existing`, `incremental sync`, and `full re-run`
- repeat analysis no longer defaults as blindly toward full reruns
- `since_last_sync` is wired into the user-facing flow

## Priority 2: GitHub Import Retry and Network Resilience

**Status:** Completed

### Goal

Make real-repository import more robust to transient GitHub or TLS failures.

### Why This Comes Next

Recent live testing showed that some import failures are not repository-specific logic bugs, but transient network/TLS failures such as:

- SSL EOF while reading
- temporary request interruption during GitHub fetches

Current import behavior is too brittle:

- one transient fetch failure can fail the whole import
- failure messaging is too generic
- there is little distinction between repo-analysis failure and network transport failure

### Scope

- add bounded retries with backoff for GitHub client requests
- handle transient `httpx` read/connect/SSL transport failures more gracefully
- classify network-origin failures separately from broader analysis failures
- improve failure summaries so users can tell when retrying is reasonable

### Expected Outcome

- fewer failed live imports
- fewer user-facing "analysis failed" messages caused by temporary network conditions
- more confidence when importing real open-source repositories

### Completed Outcome

This priority is now implemented:

- GitHub transport requests use bounded retry for transient read/connect/TLS-style failures
- retry exhaustion is classified as `network_failure`
- malformed repo input and repository-access failures still fail fast
- import summaries now distinguish network-origin failures from repository/provider/generic failures

## Priority 3: Drift Precision

**Status:** Current priority

### Goal

Move drift from "useful but noisy" toward "credible review signal."

### Why This Is Third

Drift already works end-to-end:

- accepted decisions can be evaluated
- alerts are created
- alerts are visible in the UI

But current alerts are still broad:

- `possible_supersession` can over-trigger
- broad docs such as changelogs or contributing material can appear overly relevant
- some alerts feel more like "related artifact found" than "decision likely changed"

### Scope

- tighten supersession heuristics
- reduce broad-document false positives
- improve drift alert wording and confidence semantics
- better distinguish "worth reviewing" from "likely superseded"

### Expected Outcome

- higher trust in drift alerts
- less noisy review load
- better downstream product credibility

## Updated Execution Order

```text
1. Drift precision
2. Why-search retrieval quality
3. Indexing modernization for real evidence
```

## Why This Order Now

The already-finished work removed the two biggest operational friction points:

- repeated full reruns for known workspaces
- transient GitHub transport failures that looked like generic analysis failure

The remaining highest-signal product gap is now:

1. drift alert quality after the imported-repository loop is stable
2. retrieval quality for why-answers that are still sparse or partially supported
3. deeper indexing work that improves long-term evidence quality

## What Not To Prioritize First

The following are still valid future areas, but should not come before the three priorities above:

- user account binding for workspace ownership
- deeper indexing modernization
- large retrieval architecture rewrites
- broad new source ingestion beyond GitHub
- major why-search redesign beyond the already completed focus and support grading work

## Summary

The next phase should optimize the real-repository product loop rather than expand sideways:

- improve drift precision
- strengthen why-search retrieval quality where accepted coverage is still thin
- modernize indexing only after the more direct product bottlenecks are addressed

That path should produce the strongest near-term improvement in both product quality and operational efficiency.
