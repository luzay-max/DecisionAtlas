# FAQ

## What problem does DecisionAtlas solve?

Engineering decisions are usually scattered across issues, pull requests, ADRs, and chat notes. DecisionAtlas turns that scattered context into one searchable decision memory.

## Do I need to train a model?

No. The MVP uses provider APIs and focuses on data modeling, retrieval, review workflow, and citations.

## Is every extracted decision automatically trusted?

No. Extracted decisions enter the system as `candidate` and require human review.

## Can the system answer with no evidence?

It is designed not to. The why-query path is citation-first and can return an insufficient-evidence style fallback instead of guessing.

## What does drift detection do today?

The current MVP supports:

- rule-first alerts for high-signal contradictions such as violating a cache-only Redis rule
- semantic drift enrichment for conservative labels such as `possible_supersession` and `needs_review`

It is not a continuous Git watcher yet. Today it compares accepted decisions against later imported artifacts inside a workspace when drift evaluation is run.

Imported drift is now more usable than it was earlier in the project:

- repeated weak follow-up alerts are grouped more compactly
- reevaluation replaces stale earlier alert generations
- implementation-heavy maintenance work is less likely to be surfaced as strong decision replacement

It is still conservative by design and may under-report rather than overstate repository change.

## What is missing from the MVP?

- production auth and permissions
- org-wide connectors beyond GitHub and local docs
- mature async job orchestration
- hosted GitHub App and webhook sync
- release screenshots and final public launch polish

## Is `.docx` supported?

Yes, optionally. `.docx` import depends on `pandoc` being installed locally.

## How do I run the demo validation?

Use:

```powershell
python scripts/ci/run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

For a quick real-repo smoke check, start the real stack and validate one imported public repository such as `browser-use/browser-use`:

- confirm the imported workspace reaches an explicit bounded state such as `review_ready`, `why_ready`, `evidence_limited`, or `conversion_limited`
- ask at least one focused why-question and confirm the answer contains citations
- run drift evaluation once and confirm the resulting state is understandable

## Does live analysis support any repository?

Not yet. This phase supports one-off analysis of public GitHub repositories only.

- no private repository auth
- no GitHub App installation flow
- no persistent multi-repository connection management

If a repository is thin on ADRs, docs, or rationale, the correct outcome may be `insufficient_evidence` rather than a rich answer set.

The imported workspace may also explicitly stop at:

- `review_required`
- `evidence_limited`
- `conversion_limited`

Those are intended bounded product outcomes, not necessarily runtime failures.

## What does the fake/live provider switch change?

It changes the provider used for the next real analysis or future extraction run. It does not rewrite the demo data or imported results that are already on screen.

## What makes imported why-search trustworthy?

Imported why answers are only meant to be trusted when:

- the workspace already has accepted decisions
- the answer is anchored to one accepted decision
- citations support that accepted decision

Artifact chunks can now strengthen support, but they do not replace the accepted decision as the trust anchor.
