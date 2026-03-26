# Real Repository Validation Baseline

This document defines the public-repository baseline for the real imported-workspace lane.

It has two purposes:

1. keep a small, repeatable set of repositories for real-lane validation
2. record the current sparse-evidence and failure patterns before behavior changes

## Curated Repositories

### `encode/httpx`

- Repo: `encode/httpx`
- Workspace slug: `github-encode-httpx`
- Why it matters: doc-heavy library with public rationale in docs, issues, and release notes
- Expected signals:
  - at least `3` candidate decisions after import
  - imported markdown should include README plus architecture, migration, release, or changelog style documents when present
  - review queue should contain at least one candidate with rationale-bearing citations
  - live analysis outcome may still be `ok` or `insufficient_evidence`, but it should not feel like an operational failure

### `fastapi/fastapi`

- Repo: `fastapi/fastapi`
- Workspace slug: `github-fastapi-fastapi`
- Why it matters: large framework with mixed issue, PR, and documentation evidence
- Expected signals:
  - at least `2` candidate decisions after import
  - imported workspace should surface whether the next action is review or evidence follow-up
  - why-search should only become trustworthy after accepted decisions exist

### `Textualize/rich`

- Repo: `Textualize/rich`
- Workspace slug: `github-textualize-rich`
- Why it matters: public repo with thinner explicit rationale than the guided demo
- Expected signals:
  - at least `1` candidate decision after import
  - `insufficient_evidence` remains a valid outcome, but the workspace should explain why the run is sparse
  - drift should remain interpretable even when there are no alerts

### `n8n-io/n8n`

- Repo: `n8n-io/n8n`
- Workspace slug: `github-n8n-io-n8n`
- Why it matters: large public repository that already exposed a `screened-in -> candidate` conversion bottleneck in live testing
- Expected signals:
  - at least `10` screened-in artifacts on a healthy real-analysis run
  - zero candidates is no longer enough information by itself; the run must explain whether it is evidence-limited or conversion-limited
  - `conversion_limited` is an acceptable readiness outcome until full extraction quality improves further

## Current Sparse-Evidence Patterns

These are the patterns we want to improve without pretending every public repo is rich in rationale.

### 1. Import succeeds but downstream readiness is unclear

Current imported workspaces can finish successfully and still feel inert because the UI mostly shows raw counts, latest import summary, and a generic low-signal hint.

Observed symptoms:

- users do not know whether the right next step is review, why-search, or drift evaluation
- successful sparse runs can look too similar to failed runs
- imported workspaces with some evidence still do not clearly explain what the evidence is useful for

### 2. Repository document coverage is still narrow

Current markdown selection is conservative, but it still misses some rationale-bearing files such as migration, rollout, release, operations, or deprecation notes when they are not named like the small top-level allowlist.

Observed symptoms:

- imports may include README and a few docs but still miss the documents where change rationale is actually described
- candidate extraction is skewed toward issues and PRs even when documentation carries stronger explanations

### 3. Why-search trust is easy to misread in imported workspaces

Imported why-search is only trustworthy when accepted decisions exist and the answer is grounded in those decisions. Today the read model does not guide that strongly enough.

Observed symptoms:

- users can ask why-questions before the workspace has accepted decisions
- a weak or blocked answer feels like product failure instead of an expected "review-first" state
- imported workspaces need an explicit distinction between `review_required` and `evidence_limited`

### 4. Drift exists conceptually but is not operational enough

Drift evaluation is available through the API, but imported workspaces do not yet expose whether drift has ever been evaluated or whether "no alerts" means "not evaluated" or "evaluated and clean".

Observed symptoms:

- drift page can look empty without explaining whether evaluation ran
- imported workspaces need a manual evaluate action with state and freshness

### 5. Provider and network failures can still obscure outcome quality

Live provider or network issues can still terminate analysis even when the repository itself might have been useful.

Observed symptoms:

- provider connectivity failures are visible as operational failures
- users may not separate provider/runtime problems from repository-signal problems

### 6. Screened-in artifacts can still fail to convert into candidates

Recent `n8n-io/n8n` runs showed that throughput and visibility can improve while candidate yield remains at zero.

Observed symptoms:

- the run can shortlist and screen in many artifacts, complete full extraction attempts, and still create no candidate decisions
- the product needs to expose that full extraction quality, not only repository evidence coverage, limited the result
- future validation should compare `screened_in_artifacts` against `created_candidates`, not just import completion and candidate totals

## Validation Use

When changing the real imported-workspace lane, compare behavior against this baseline:

- did document coverage improve on the curated repos without broad noisy ingest?
- did at least one next action become obvious after import?
- did why-search become clearer about review-required versus evidence-limited?
- did drift become explicitly evaluable and interpretable?
- did the product reduce "import worked, but I still do not know what to do" outcomes?
