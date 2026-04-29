# Real Repository Validation Baseline

This document defines the public-repository baseline for the real imported-workspace lane.

It has two purposes:

1. keep a small, repeatable set of repositories for real-lane validation
2. record the current bounded outcomes and remaining weak spots before behavior changes

## Curated Repositories

The runnable fixture entrypoint is `examples/live-benchmarks/`:

- `repositories.json` captures repo-level import/readiness expectations.
- `why-cases.json` captures focused imported why-search checks.
- `drift-cases.json` captures known drift-noise regression checks.

The default benchmark command validates those fixtures offline:

```powershell
python scripts/ci/run_benchmark.py
```

This offline fixture validation is part of the canonical local release baseline gate via:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

Optional live why-case smoke checks can run against an already-started local stack and already-existing imported workspaces:

```powershell
python scripts/ci/run_benchmark.py --live-real-repos
```

This live mode is an operator-guided confidence layer. It is not part of the default release gate because it depends on local stack availability, provider configuration, existing imported workspaces, network behavior, and repository state.

By default, live mode writes a structured report to:

```text
.tmp/live-real-repo-validation-report.json
```

Use a custom path when you want to preserve a dated report:

```powershell
python scripts/ci/run_benchmark.py --live-real-repos --live-real-repos-report .tmp/live-real-repo-validation-2026-04-24.json
```

The report records one row per curated repository with:

- repo id, repo name, and workspace slug
- observed bounded outcome such as `review_ready`, `why_ready`, `evidence_limited`, `conversion_limited`, `analysis_failed`, `missing_workspace`, or `operational_failure`
- dashboard readiness, review state, why state, drift state, next action, and recommended actions
- candidate, accepted, total decision, and screened-in artifact counts when available
- focused why-case status, citation count, and failure reason when applicable
- drift state and forbidden drift-case checks when applicable
- explicit operational errors when the API, provider, network, or local workspace state blocks validation

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
  - at least `1` reviewable candidate on the current protected baseline
  - if the run still underperforms, it must explain whether it is evidence-limited, conversion-limited, or otherwise operationally bounded
  - `conversion_limited` remains a bounded diagnostic state, but it is no longer the intended baseline expectation for this repo

### `browser-use/browser-use`

- Repo: `browser-use/browser-use`
- Workspace slug: `github-browser-use-browser-use`
- Why it matters: imported lane regression repo with strong real-world why and drift examples
- Fixture coverage:
  - `examples/live-benchmarks/why-cases.json`
  - `examples/live-benchmarks/drift-cases.json`
- Expected signals:
  - imported readiness should expose explicit review / why / drift state
  - focused why-questions around HTTP downloads and keep-alive shutdown behavior should be able to reach `ok` with citations after accepted decisions exist
  - equivalent focused why phrasing around HTTP download status should still land on the same accepted rationale thread
  - live why-case reports should record the observed primary decision title so retrieval regressions are visible even when answer terms still match
  - drift should stay conservative on implementation-heavy follow-up fixes

## Current Baseline Patterns

These are the patterns we want to preserve or improve without pretending every public repo is rich in rationale.

### 1. Import now succeeds into clearer downstream readiness

Imported workspaces now expose clearer review / why / drift readiness and recommended actions.

Current expectation:

- users should be able to tell whether the next step is review, why-search, drift evaluation, or import-summary inspection
- successful sparse runs should not look like generic failures
- dashboard and search should agree on the readiness interpretation
- imported review cards should expose enough source-ref coverage, preview quote, primary artifact provenance, and first-baseline guidance for a reviewer to decide whether the first accepted decision is safe to establish

### 2. Repository document coverage is still selective

Current markdown selection is stronger than the earlier MVP baseline, but it should still remain selective enough to avoid broad noisy ingest.

Current expectation:

- imports should include rationale-bearing docs such as migration, rollout, release, operations, or deprecation notes when present
- coverage improvements should not degrade into broad low-signal ingest

### 3. Imported why-search is stronger but still bounded by accepted-decision grounding

Imported why-search is now clearer and stronger, but it still depends on accepted-decision grounding.

Current expectation:

- users can still ask why before review is complete, but the product should clearly explain `review_required`
- focused why-questions should prefer one accepted decision as the anchor
- technically equivalent focused why phrasings should still resolve to the same accepted rationale thread on the curated regression cases
- supporting artifact chunks may strengthen support, but should not replace the accepted decision as the answer anchor

### 4. Drift is more operational, but should remain conservative

Imported drift is now manually evaluable and more interpretable.

Current expectation:

- drift state should distinguish `unevaluated`, `stale`, `clean`, and alert-present paths
- grouped weak alerts should stay compact
- implementation-heavy maintenance fixes should not easily escalate into strong replacement signals

### 5. Provider and network failures are clearer, but still matter

Live provider or network issues can still terminate analysis even when the repository itself might have been useful.

Current expectation:

- provider connectivity failures are visible as operational failures
- users should be able to distinguish retryable network problems from repository-signal problems

### 6. Screened-in artifacts can still fail to convert into candidates

Recent `n8n-io/n8n` runs showed that throughput and visibility can improve while candidate yield remains at zero.

Current expectation:

- the run can shortlist and screen in many artifacts, complete full extraction attempts, and still create no candidate decisions
- the product needs to expose that full extraction quality, not only repository evidence coverage, limited the result
- future validation should compare `screened_in_artifacts` against `created_candidates`, not just import completion and candidate totals

## Validation Use

Treat validation in two layers:

- default release baseline: canonical local pre-release script plus offline fixture benchmark validation
- optional operator-guided validation: live imported-workspace smoke checks against curated public repos

The optional live layer improves confidence before a milestone or external demo, but it should not be confused with the stable offline release gate.

Interpret live validation results as follows:

- `review_ready`: the imported workspace has reviewable candidates and needs human acceptance before downstream why/drift can be trusted
- `why_ready`: at least one accepted imported baseline exists, but individual why answers still need question-level grounding
- `evidence_limited`: the repo imported successfully but did not expose enough rationale-bearing signal for the requested path
- `conversion_limited`: the run screened in enough artifacts but still failed to produce reviewable candidates after extraction attempts
- `analysis_failed`: the product recorded a failed analysis state
- `missing_workspace`: the local stack does not currently have the expected imported workspace
- `operational_failure`: the validation request failed because of API availability, auth/session state, provider configuration, network, or another runtime condition

Latest local live validation attempt:

- Date: 2026-04-24
- Command: `python scripts/ci/run_benchmark.py --live-real-repos`
- Report path: `.tmp/live-real-repo-validation-report.json`
- Result: blocked by operational precondition; local API at `http://127.0.0.1:3001` was not running, so all curated repositories were classified as `operational_failure`
- Interpretation: this confirms the live report can distinguish unavailable local stack state from repository evidence quality; it is not a real-repo product outcome measurement

When changing the real imported-workspace lane, compare behavior against this baseline:

- did document coverage improve on the curated repos without broad noisy ingest?
- did at least one next action become obvious after import?
- did why-search remain anchored to accepted decisions while improving support quality?
- did drift remain explicitly evaluable and interpretable without reintroducing broad noise?
- did the product reduce "import worked, but I still do not know what to do" outcomes?
- if the behavior is important enough to protect, did it get captured in `examples/live-benchmarks/` rather than only in prose?
