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

## Status Update (2026-04-09)

Since the 2026-04-01 update, the next two quality slices have also shipped:

- `drift precision` is complete across multiple follow-up changes:
  - weaker follow-up alerts are grouped more compactly
  - `possible_supersession` is more conservative
  - stale prior drift alerts are replaced during reevaluation
  - implementation-heavy maintenance work is less likely to surface as a strong replacement signal
- `why-search retrieval quality` is complete:
  - query rewrite is stronger for technical aliases
  - hybrid retrieval gives vector evidence more weight
  - chunk-backed supporting evidence now helps imported why answers reach `ok`
- `imported workspace readiness surface` is complete:
  - dashboard and search now show richer imported-workspace readiness
  - review / why / drift next actions are surfaced more explicitly

This means the practical next-work order has changed again:

```text
1. Indexing modernization for real evidence
2. Release-quality cleanup
3. Lightweight real-repo benchmark capture
4. v0.3 platform work
```

## Status Update (2026-04-09, later)

Since the earlier 2026-04-09 update, `indexing modernization for real evidence` has also shipped:

- structure-aware chunking now preserves section context
- oversized sections use bounded overlap instead of blind flat slicing
- artifact chunks now persist structured metadata
- imported why answers can rank structured chunk evidence above weaker flat chunks while keeping accepted decisions as the answer anchor

That changes the practical next-work order again:

```text
1. Release-quality cleanup
2. Lightweight real-repo benchmark capture
3. v0.3 platform work
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

**Status:** Completed

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

### Completed Outcome

This priority is now implemented:

- broad-document and weak follow-up drift noise is lower
- grouped weak follow-up alerts are more compact
- reevaluation replaces stale prior alerts instead of rendering conflicting generations together
- implementation-heavy fixes are less likely to be misread as strong replacement signals

## Priority 4: Why-Search Retrieval Quality

**Status:** Completed

### Goal

Improve imported why-answer recall and evidence thickness without changing the accepted-decision trust anchor.

### Why This Came Next

Once drift precision improved, the next product-quality gap was imported why answers that still felt too sparse even when the right accepted decision existed.

### Scope

- strengthen query rewrite and technical alias normalization
- rebalance hybrid retrieval so vector evidence matters more
- let chunk-backed artifact evidence support the accepted-decision answer
- preserve the rule that accepted decisions remain the answer anchor

### Completed Outcome

This priority is now implemented:

- imported why answers now use stronger query normalization
- chunk-backed supporting evidence can raise some imported answers from `limited_support` to `ok`
- accepted decisions remain the primary answer anchor

## Priority 5: Imported Workspace Readiness Surface

**Status:** Completed

### Goal

Make imported workspaces explain what the user should do next instead of showing only sparse status counts.

### Why This Followed

The imported lane had become operationally stronger, but the product still needed to say more clearly whether the workspace was ready for review, why-search, or drift follow-up.

### Scope

- expose richer imported readiness payloads from the backend
- surface explicit recommended actions
- keep dashboard and search aligned on the same readiness semantics

### Completed Outcome

This priority is now implemented:

- imported readiness now includes review, why, and drift-oriented state
- recommended actions are surfaced consistently in dashboard and search
- imported workspaces better explain what the next useful action is

## Updated Execution Order

```text
1. Release-quality cleanup
2. Lightweight real-repo benchmark capture
3. v0.3 platform work
```

## Why This Order Now

The already-finished work removed the earlier operational and product-semantics bottlenecks:

- repeated full reruns for known workspaces
- transient GitHub transport failures that looked like generic analysis failure
- broad and repetitive drift noise in the imported-repo loop
- sparse why answers caused by weak imported retrieval support
- vague imported-workspace next-step semantics

The remaining highest-signal product gap is now:

1. release cleanup so the current product baseline is documented and presentable
2. lightweight benchmark capture so future regressions are easier to catch without turning validation into a large separate project
3. heavier platform work only after the current loop is cleaner and better packaged

## What Not To Prioritize First

The following are still valid future areas, but should not come before the three priorities above:

- GitHub App auth and webhook sync
- private repository support
- login, roles, and workspace scoping
- broad new source ingestion beyond GitHub
- large retrieval architecture rewrites before indexing quality is improved

## Summary

The next phase should improve release polish and lightweight validation rather than immediately expand into heavier platform features:

- do a release-quality cleanup pass
- capture a lightweight real-repo benchmark set as a supporting validation asset
- postpone heavier v0.3 platform work until after the current loop is better packaged and easier to validate

That path should produce the strongest near-term improvement in both product quality and operational efficiency.
