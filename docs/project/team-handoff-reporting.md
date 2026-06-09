# Team Handoff Reporting

[Home](../../README.md) | [Self-Hosted Package](self-hosted-package-guide.md) | [Readiness Checklist](self-hosted-readiness-checklist.md) | [Evidence History](../evidence/readiness/index.md)

---

Use the team handoff report when a DecisionAtlas workspace is ready to be reviewed by a team lead, customer, or self-hosted operator. The report is a bounded delivery snapshot, not a live dashboard.

## What It Includes

- Workspace and repository scope.
- Release evidence status.
- Hosted/operator readiness status.
- Real-repo benchmark comparison.
- Readiness evidence history.
- Self-hosted package verification.
- Clean self-hosted install rehearsal evidence when provided.
- License/support boundary evidence when provided.
- Public GitHub import rehearsal evidence when available.
- Compact review/audit history when provided.
- Limitations and next actions.

## Generate Report

From the repository root:

```powershell
python scripts\ci\collect_team_handoff_report.py `
  --label self-hosted-team-handoff `
  --version-label <version-or-date> `
  --workspace-slug <workspace> `
  --repository-provider github `
  --repository-access-mode public `
  --repository <owner/repo> `
  --repository-authorization-status authorized `
  --release-evidence-json .tmp\release-evidence.json `
  --hosted-readiness-json .tmp\hosted-operator-readiness.json `
  --benchmark-comparison-json .tmp\real-repo-benchmark-comparison.json `
  --readiness-history-index-json docs\evidence\readiness\index.json `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --clean-install-rehearsal-json .tmp\clean-self-hosted-install-rehearsal.json `
  --license-support-json templates\self-hosted-entitlement.example.json `
  --public-github-import-json .tmp\public-github-import-rehearsal.json `
  --output-json .tmp\team-handoff-report.json `
  --output-markdown .tmp\team-handoff-report.md
```

If optional evidence is not available, omit the flag. The report will record that section as `not_provided` instead of silently treating it as pass.

## Secret Boundary

Do not provide raw tokens, `.env` files, database dumps, private repository archives, raw model prompts, or unbounded local logs as report input.

The generator redacts token-like and secret-like values, but operators should still pass curated evidence JSON rather than raw private artifacts.

## Clean Handoff Checklist

- OpenSpec strict validation is green.
- Release evidence is generated.
- Hosted/operator readiness is generated.
- Benchmark comparison is generated or explicitly accepted as not provided.
- Self-hosted package verification is generated.
- Clean self-hosted install rehearsal is generated before claiming external operator trial readiness.
- License/support boundary evidence is attached for paid customer handoff or explicitly disclosed as missing/operator-guided.
- Readiness evidence history has a durable entry when making a customer-ready claim.
- The Markdown handoff report is readable by a human without a running backend.
