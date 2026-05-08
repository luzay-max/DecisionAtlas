# Demo Script

[Home](../README.md) | [Quick Start](quick-start.md) | [Deployment](deployment.md) | [FAQ](faq.md) | [Hosted Operator Guide](hosted-demo-operator-guide.md) | [Hosted Preview Readiness](hosted-preview-readiness.md) | [中文](demo-script_zh-CN.md)

---

This walkthrough is designed for a **60-90 second product demo**. The primary story is the stable guided lane, with optional governed-preview and real-repo credibility checks at the end.

Before a hosted walkthrough, run the operator health and smoke checks from [Hosted Demo Operator Guide](hosted-demo-operator-guide.md), then record the result with [Hosted Preview Readiness](hosted-preview-readiness.md). If the seeded workspace has drifted, reset `demo-workspace` before starting the public flow.

For external hosted preview, do not start with live repository import or governance setup. Start with `demo-workspace`, then optionally show the governed second act and imported/platform lanes after explaining their human-review, provider, credential, and network dependencies.

### Opening Posture

**Route**: `http://localhost:3000/`

**Narration**:
> "Tonight's main path is the guided demo. It uses seeded walkthrough data so the product story stays stable."
> "Live analysis and provider controls still exist, but they are intentionally moved into an advanced section."

### Step 1: Open the Guided Demo Workspace

**Route**: `http://localhost:3000/workspaces/demo-workspace`

**Narration**:
> "The dashboard is now the walkthrough control panel. It tells us which step we are on and what to do next."
> "The provenance banner makes it explicit that this workspace is seeded demo data, not imported repository output."

### Step 2: Confirm the Demo Workspace Is Ready

**Route**: `http://localhost:3000/workspaces/demo-workspace`

**Narration**:
> "The stable demo workspace is seeded. We do not run a real import inside this lane."
> "Once the workspace is ready, the UI points directly to the review step."

### Step 3: Show the Review Queue

**Route**: `http://localhost:3000/review?workspace=demo-workspace`

**Narration**:
> "Candidate decisions are not auto-promoted. The review step makes the human checkpoint explicit."
> "The page explains the goal of this step and hands us off directly to why-search when we're done."

### Step 4: Show Why-Search

**Route**: `http://localhost:3000/search?workspace=demo-workspace`

**Suggested Question**: `why use redis cache`

**Narration**:
> "Why-search starts from a recommended demo question, so we do not need to improvise."
> "When evidence exists, the answer includes citations. When it doesn't, the system fails closed instead of bluffing."

### Step 5: Show the Timeline

**Route**: `http://localhost:3000/timeline?workspace=demo-workspace`

**Narration**:
> "Accepted decisions become a time-ordered memory instead of disappearing into issues and pull requests."
> "The guided demo framing keeps the story moving and points clearly to the drift step."

### Step 6: Show Drift Alerts and Close

**Route**: `http://localhost:3000/drift?workspace=demo-workspace`

**Narration**:
> "Drift makes the memory operational by checking newer artifacts against accepted decisions."
> "The last step closes the loop and makes it obvious that we completed the demo lane."

### Closing Line

> "DecisionAtlas is not training a new model. It is turning engineering decisions into durable, reviewable, searchable operating memory."

### Optional: 45-Second Governed Preview Proof

This is a **bounded second act**, not a replacement for the guided demo.

**Route**: `http://localhost:3000/governance`

**Narration**:
> "The next layer is governance memory. Human-authored Markdown standards, roadmaps, postmortems, and decisions can be imported as governance context."
> "The system creates rule drafts, but it does not accept them automatically. A human reviews the draft, keeps the source excerpt, and records rationale."
> "Accepted rules become context for local governance checks and the AI-agent guardrail."

**Guardrail command**:

```powershell
python scripts\governance\agent_guardrail.py --summary
```

**Narration**:
> "`continue` means no blocking governance concern was found. `caution` means we disclose or address advisory evidence. `pause` means the agent must ask a human before continuing."
> "The guardrail is advisory by default. It does not rewrite code, mutate specs, accept rules, or block CI."

### Optional: 30-Second Real-Repo Proof

This is an **operator-guided credibility check**, not part of the core guided walkthrough.

**Route**: `http://localhost:3000/`

**Narration**:
> "The seeded lane is our stable walkthrough, but the same product can also analyze a real public GitHub repository into a separate imported workspace."
> "That imported workspace now exposes whether review, why-search, and drift are ready, instead of leaving the operator to guess."
> "Imported why answers stay anchored to accepted decisions, with artifact chunks acting as supporting evidence."
> "We use this as a bounded proof of real capability, not as the primary demo story."
> "If we generated a live benchmark report, it stays as dated operator evidence rather than a committed `.tmp` artifact."

---

### Quick Reference

| Step | Route | Key Point |
|------|-------|-----------|
| 1 | `/workspaces/demo-workspace` | Walkthrough control panel |
| 2 | `/workspaces/demo-workspace` | Seeded workspace readiness |
| 3 | `/review?workspace=demo-workspace` | Human checkpoint |
| 4 | `/search?workspace=demo-workspace` | Citation-first answers |
| 5 | `/timeline?workspace=demo-workspace` | Time-ordered decision memory |
| 6 | `/drift?workspace=demo-workspace` | Operational drift detection |
| Optional | `/governance` | Human-reviewed governance rules |
| Optional | local guardrail command | Advisory agent handoff |
