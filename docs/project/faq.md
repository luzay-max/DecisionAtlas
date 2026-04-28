# FAQ

[Home](../README.md) | [Quick Start](quick-start.md) | [Deployment](deployment.md) | [Demo Script](demo-script.md) | [Hosted Operator Guide](hosted-demo-operator-guide.md) | [中文](faq_zh-CN.md)

---

### What problem does DecisionAtlas solve?

Engineering decisions are usually scattered across issues, pull requests, ADRs, and chat notes. DecisionAtlas turns that scattered context into one searchable decision memory.

### Do I need to train a model?

No. The MVP uses provider APIs and focuses on data modeling, retrieval, review workflow, and citations.

### Is every extracted decision automatically trusted?

No. Extracted decisions enter the system as `candidate` and require human review before becoming trusted.

### Can the system answer with no evidence?

It is designed not to. The why-query path is citation-first and can return an `insufficient-evidence` fallback instead of guessing.

### What does drift detection do today?

The current MVP supports:

- **Rule-first alerts**: High-signal contradictions such as violating a "cache-only Redis" rule.
- **Semantic drift enrichment**: Conservative labels such as `possible_supersession` and `needs_review`.

It is not a continuous Git watcher yet. It compares accepted decisions against later imported artifacts inside a workspace when drift evaluation is run.

Imported drift is now more usable:

- Repeated weak follow-up alerts are grouped more compactly.
- Reevaluation replaces stale earlier alert generations.
- Implementation-heavy maintenance work is less likely to be surfaced as strong decision replacement.

> It is still conservative by design and may under-report rather than overstate repository change.

### What is missing from the v0.3 RC?

| Feature | Status |
|---------|--------|
| Local/bootstrap session, owner scope switching, and role gates | Included in v0.3 RC |
| GitHub App installation binding | Included as an admin/operator setup flow |
| Token-backed private repository access binding | Included as an admin/operator setup flow |
| Full SaaS org-management console | Not included |
| Secret vault and credential rotation UI | Not included |
| GitHub Marketplace/OAuth self-service installation | Not included |
| Multi-user collaborative review workflow | Not included |
| Billing | Not included |
| Org-wide connectors beyond GitHub and local docs | Planned |
| Mature async job orchestration | Planned |
| Hosted preview launch polish | Planned |

### Is `.docx` supported?

Yes, optionally. `.docx` import depends on `pandoc` being installed locally.

### How do I run validation?

```powershell
# Canonical local release baseline
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

Use individual commands only when debugging a failing phase:

```powershell
python scripts/ci/run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

For a running hosted demo environment, use the operator checks instead:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
```

These are hosted environment checks, not a replacement for the default release gate.

### Does live analysis support any repository?

Not universally. Public GitHub repository import remains the default live-analysis path.

v0.3 RC also includes admin/operator flows to bind a repository to a GitHub App installation or token-backed private access source inside the current owner scope. Those flows do not yet provide full Marketplace/OAuth self-service installation, secret vault behavior, or persistent multi-repository connection management.

If a repository is thin on ADRs, docs, or rationale, the correct outcome may be `insufficient_evidence` rather than a rich answer set.

The imported workspace may also explicitly stop at `review_required`, `evidence_limited`, or `conversion_limited`. Those are intended bounded product outcomes, not runtime failures.

### What does the fake/live provider switch change?

It changes the provider used for the **next** real analysis or extraction run. It does **not** rewrite the demo data or imported results already on screen.

### What makes imported why-search trustworthy?

Imported why answers are only meant to be trusted when:

1. The workspace already has **accepted decisions**.
2. The answer is **anchored to one accepted decision**.
3. **Citations support** that accepted decision.

Artifact chunks can strengthen support, but they do **not** replace the accepted decision as the trust anchor.
