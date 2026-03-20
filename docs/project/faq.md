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

## What is missing from the MVP?

- production auth and permissions
- org-wide connectors beyond GitHub and local docs
- mature async job orchestration
- release screenshots and polish for public launch assets

## Is `.docx` supported?

Yes, optionally. `.docx` import depends on `pandoc` being installed locally.

## How do I run the demo validation?

Use:

```powershell
python scripts/ci/run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

## Does live analysis support any repository?

Not yet. This phase supports one-off analysis of public GitHub repositories only.

- no private repository auth
- no GitHub App installation flow
- no persistent multi-repository connection management

If a repository is thin on ADRs, docs, or rationale, the correct outcome may be `insufficient_evidence` rather than a rich answer set.
