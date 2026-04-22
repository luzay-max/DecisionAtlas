# DecisionAtlas Branching And Live Data Exploration

Date: 2026-03-20
Mode: Explore
Status: Thinking captured, no implementation

## Why This Exists

The project has already passed the MVP phase and moved into `v0.2` hardening. The next challenge is no longer "what feature should exist" but "how should future work be split so the product stays coherent and credible."

At this stage, continuing on a single long-lived branch would mix together:

- product credibility work
- real capability expansion
- deployment and hosted demo work
- future platform work

That would make the codebase harder to reason about and make `main` less trustworthy as a stable demo branch.

## Recommended Branch Strategy

Treat `main` as the stable public line.

```text
main
├─ feat/clarify-demo-vs-live-data
├─ feat/expand-real-repo-ingest
├─ feat/host-public-demo
└─ feat/v0.3-auth-private-repo
```

Core rule:

- `main` contains stable, demoable, releasable work
- one branch solves one theme
- branches can be planned in parallel
- merges should happen serially

This is the intended operating model:

```text
parallel thinking
      +
serial implementation
      +
clean merges back to main
```

## Branch Definitions

### 1. feat/clarify-demo-vs-live-data

Purpose:

- Make it obvious what is demo seed data and what is real imported workspace data

Why this is first:

- Product credibility is currently the highest-risk area
- Users can already misread timeline, why-search, and drift results as real imported history

This branch should cover:

- explicit `Demo` vs `Imported` workspace labeling
- dashboard source labeling
- why-answer provenance explanation
- timeline provenance explanation
- drift provenance explanation
- homepage and demo script clarification

This branch should not cover:

- importer expansion
- hosted deployment
- auth or private repo support

This is the `product credibility` branch.

### 2. feat/expand-real-repo-ingest

Purpose:

- Improve the usefulness of real repository analysis

Why it matters:

- GitHub import is real, but many repositories do not produce enough structured decision evidence with the current import scope

This branch should cover:

- importing README / docs / ADR / markdown content from repos
- clearer import failure summaries
- better handling of thin repositories
- stronger artifact coverage for candidate extraction

This branch should not cover:

- hosted deployment
- GitHub App install flow
- login or permissions

This is the `real capability` branch.

### 3. feat/host-public-demo

Purpose:

- Turn the current local demo into a stable online demo

This branch should cover:

- true one-command bring-up
- environment and secret layout
- health checks and deployment instructions
- hosted smoke validation

This branch should not cover:

- importer redesign
- new product scope
- platform auth

This is the `delivery and presentation` branch.

### 4. feat/v0.3-auth-private-repo

Purpose:

- Move from public demo product toward platform capability

This branch belongs later because it introduces the highest complexity:

- GitHub App auth
- private repositories
- user roles
- workspace scoping

This is the `platformization` branch.

## Recommended Merge Order

```text
1. feat/clarify-demo-vs-live-data
2. feat/expand-real-repo-ingest
3. feat/host-public-demo
4. feat/v0.3-auth-private-repo
```

Reasoning:

- First fix trust and narrative clarity
- Then improve true repository usefulness
- Then publish the hosted demo
- Then add complex platform concerns

## Working Model

Use one branch per story:

```text
one branch = one story
one change = one goal
one merge = one clear outcome
```

Suggested workflow:

```text
clean main
  ↓
create feature branch
  ↓
create matching change/proposal
  ↓
implement only that theme
  ↓
test + update docs
  ↓
merge to main
```

## Current Repository Reality

The repository currently shows a small unfinished local change around timeline display:

- `apps/web/components/timeline/timeline-list.tsx`
- `apps/web/tests/timeline-page.test.tsx`

That should be cleaned up before starting the next real feature branch, otherwise the next theme will inherit unrelated state.

## Focused Exploration: clarify-demo-vs-live-data

This is the selected next theme for deeper exploration.

### The Core Problem

The product currently mixes two different truths:

```text
Truth A: stable seed data used to make the demo reliable
Truth B: real imported data from actual repositories
```

When the UI does not distinguish them, users can draw the wrong conclusion:

- "this timeline is real project history"
- "this why-answer proves the import pipeline is strong"
- "this drift alert came from a real repo change"

That weakens trust.

### The Goal

Make every important page answer this question immediately:

```text
What am I looking at right now?
- demo data?
- imported repo data?
- mixed workspace state?
```

### Product Shape

The target mental model should look like this:

```text
┌──────────────────────────────┐
│         Workspace            │
├──────────────────────────────┤
│ Type: Demo / Imported        │
│ Source: Seed / GitHub import │
│ Repo: encode/httpx           │
│ Last import: real or none    │
└──────────────────────────────┘
```

And downstream pages should inherit that framing:

```text
Dashboard  → what kind of workspace is this?
Review     → where did these candidates come from?
Why Search → what evidence pool answered this question?
Timeline   → are these seeded milestones or imported decisions?
Drift      → is this seeded demo drift or evaluated imported drift?
```

### Likely UI Impact

Dashboard:

- workspace badge: `Demo Workspace` or `Imported Workspace`
- data source summary: `Seeded demo data` vs `Imported from GitHub`
- import panel should clearly separate:
  - demo preparation state
  - real import job state

Why Search:

- answer header should indicate source context
- if answer is built from seed data, say so explicitly
- if answer is built from imported evidence, say that too

Timeline:

- each timeline page should indicate whether the decision history is:
  - seeded
  - imported
  - mixed

Drift:

- drift alerts should indicate whether the alert originated from:
  - seed scenario
  - imported artifact evaluation

Homepage:

- should stop implying that the demo workspace is automatically equivalent to a real imported repository

### Likely Data/Domain Impact

The current system probably needs an explicit concept of data provenance.

At the conceptual level:

```text
Workspace
  ├─ mode: demo | imported | mixed
  └─ source summary

Decision
  └─ provenance: seeded | extracted

Artifact
  └─ provenance: seeded | imported

Alert
  └─ provenance: seeded-scenario | evaluated-from-import
```

Whether that should become hard schema or computed metadata is a later implementation decision. The important discovery is that the UI problem is downstream of a provenance problem.

### Important Non-Goals

This change should not try to solve:

- better extraction quality
- broader import coverage
- hosted deployment
- auth
- private repos

If it starts doing those things, the branch loses its point.

### What Good Looks Like

A user should be able to open any major page and understand within a few seconds:

1. whether this is demo data or imported data
2. where the current answer/timeline/alert came from
3. what the system has really proven versus what is being demonstrated

### Exit Criteria For This Change

This branch is complete when:

- the demo workspace is explicitly labeled as demo
- imported workspaces are visually distinct from demo workspaces
- why-search, timeline, and drift each communicate provenance
- homepage and docs stop blurring demo behavior with real import behavior
- user confusion between seeded and imported data is materially reduced

## Recommended Next Decision

When leaving explore mode, the next concrete move should be:

1. clean the current local timeline fix
2. create branch `feat/clarify-demo-vs-live-data`
3. create a matching change proposal
4. implement only that theme

## Summary

The project should continue on multiple branches, but not by mixing themes in one line of work.

The most important next branch is:

- `feat/clarify-demo-vs-live-data`

Because before the project becomes more capable, it needs to become more trustworthy.
