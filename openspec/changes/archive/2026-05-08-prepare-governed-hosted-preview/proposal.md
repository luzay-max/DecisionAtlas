## Why

DecisionAtlas now has a stronger local governance loop, agent guardrail workflow, demo recovery path, and real-repository value benchmark, but the externally hosted preview story still reads mostly like generic service readiness. Stage 12 should turn the current baseline into a governed hosted preview that an operator can verify quickly, recover safely, and explain without overstating production SaaS readiness.

## What Changes

- Extend hosted preview readiness from health/smoke/recovery checks into a governed pre-demo checklist that includes governance Markdown ingest, accepted-rule review boundaries, agent guardrail smoke, and optional real-repository value report evidence.
- Update the external walkthrough narrative so the stable public lane remains `demo-workspace`, while the governance story is presented as a bounded second act: project docs become reviewable rules, accepted rules inform the guardrail, and guardrail output guides AI-agent handoff.
- Clarify how `continue`, `caution`, and `pause` guardrail states should be interpreted during hosted preview preparation and external demos.
- Record that generated live real-repository benchmark reports remain optional credibility evidence and should be summarized or attached by operators rather than treated as a required public walkthrough step.
- Keep hosted preview readiness separate from default release validation and avoid introducing default CI enforcement, billing, full org administration, secret vault, or marketplace self-service claims.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `hosted-demo-operator-flow`: Add governed hosted preview readiness requirements covering governance smoke checks, operator recovery, result classification, and optional real-repository value evidence.
- `guided-demo-experience`: Clarify the external walkthrough structure so the guided demo remains the primary public lane and the governance story is a bounded optional extension.
- `governance-markdown-ingest`: Document and validate the hosted-preview demo boundary for importing governance Markdown as human-reviewed rule drafts, not automatic policy.
- `ai-agent-governance-guardrails`: Require hosted-preview operator guidance for guardrail smoke results, caution/pause disclosure, and advisory-only semantics.
- `lightweight-real-repo-benchmarks`: Clarify that live value benchmark reports are optional hosted-preview credibility artifacts and remain outside the stable public walkthrough and default CI.
- `release-baseline-validation`: Preserve the distinction between governed hosted preview readiness and mandatory release-gate validation.

## Impact

- Documentation and readiness reports under `docs/project/`, especially hosted preview, hosted operator, demo script, release checklist, and governance guardrail guidance.
- Optional operator commands under existing `scripts/demo/`, `scripts/governance/`, and `scripts/ci/run_benchmark.py`; script changes should be minimal and only added if the readiness workflow exposes an actual command gap.
- OpenSpec specs for hosted operator flow, guided demo experience, governance Markdown ingest, agent guardrails, lightweight real-repo benchmarks, and release validation boundaries.
- No product runtime dependency changes are expected, and no default CI or enforcement-mode changes are in scope.
