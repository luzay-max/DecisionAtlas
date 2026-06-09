# Self-Hosted Release Package Guide

[Home](../../README.md) | [Deployment](deployment.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Delivery Rehearsal](self-hosted-delivery-rehearsal.md) | [Operations Runbook](self-hosted-operations-runbook.md)

---

Use this guide when preparing a DecisionAtlas package for a private server, paid pilot, or small-team self-hosted evaluation.

The package is a source-tree handoff bundle, not a binary installer. It contains selected docs, startup and validation scripts, an environment template, and a machine-readable manifest. It does not include customer secrets, databases, imported repositories, node modules, virtual environments, or local scratch output.

For external evaluation, start with [Pilot Customer Delivery Kit](pilot-customer-delivery-kit.md). It provides the one-page product explanation, demo script, deployment checklist, FAQ, tier comparison, and delivery email template that should accompany the technical package.

## Package Layout

Expected layout:

```text
decisionatlas-self-hosted/
  manifest.json
  README.md
  templates/
    self-hosted.env.example
    self-hosted-entitlement.example.json
  docs/
    project/
      deployment.md
      quick-start.md
      self-hosted-readiness-checklist.md
      self-hosted-delivery-rehearsal.md
      self-hosted-commercial-baseline.md
      pilot-customer-delivery-kit.md
      pilot-demo-script.md
      pilot-deployment-checklist.md
      pilot-customer-faq.md
      pilot-tier-comparison.md
      pilot-delivery-email-template.md
      self-hosted-operations-runbook.md
      team-handoff-reporting.md
      self-hosted-license-and-support-boundary.md
      release-checklist.md
  scripts/
    dev/
      start-real-stack.ps1
      start-real-stack.bat
      stop-real-stack.ps1
      stop-real-stack.bat
    ci/
      pre-release.ps1
      collect_release_evidence.py
      collect_readiness_evidence_history.py
      collect_team_handoff_report.py
      verify_pilot_customer_delivery_kit.py
      rehearse_clean_self_hosted_install.py
    demo/
      check_seeded_demo.py
      collect_hosted_readiness.py
      health-check.ps1
      smoke-check.ps1
```

## Build Package

From the repository root:

```powershell
python scripts\ci\build_self_hosted_package.py `
  --label decisionatlas-self-hosted `
  --version-label self-hosted-preview `
  --commit <commit>
```

Default output:

```text
.tmp/self-hosted-package/decisionatlas-self-hosted/
```

## Verify Package

Run the offline package verifier:

```powershell
python scripts\ci\verify_self_hosted_package.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --output-json .tmp\self-hosted-package-verification.json `
  --output-markdown .tmp\self-hosted-package-verification.md
```

The verifier checks package structure and manifest integrity. It does not start Docker, validate live credentials, import private repositories, or run a live benchmark. Those remain separate rehearsal evidence.

Verify the pilot customer materials:

```powershell
python scripts\ci\verify_pilot_customer_delivery_kit.py `
  --output-json .tmp\pilot-customer-delivery-kit-verification.json `
  --output-markdown .tmp\pilot-customer-delivery-kit-verification.md
```

## Rehearse Clean Install

Run the clean install rehearsal after package verification and before claiming that an external operator can trial the package:

```powershell
python scripts\ci\rehearse_clean_self_hosted_install.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --release-evidence-json .tmp\release-evidence.json `
  --hosted-readiness-json .tmp\hosted-operator-readiness.json `
  --benchmark-comparison-json .tmp\real-repo-benchmark-comparison.json `
  --readiness-history-json docs\evidence\readiness\index.json `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --public-github-import-json .tmp\public-github-import-rehearsal.json `
  --license-support-json templates\self-hosted-entitlement.example.json `
  --team-handoff-json .tmp\team-handoff-report.json `
  --output-json .tmp\clean-self-hosted-install-rehearsal.json `
  --output-markdown .tmp\clean-self-hosted-install-rehearsal.md
```

The clean rehearsal copies the package into `.tmp/clean-self-hosted-install/<label>/package-copy`, checks operator handoff entry points, preserves missing or non-pass evidence states, and writes operator-readable Markdown. Package verification is necessary but not sufficient for clean customer handoff.

## Operator Setup

1. Install Docker Desktop or equivalent PostgreSQL and Redis services.
2. Copy `templates/self-hosted.env.example` to `.env` on the operator-controlled host.
3. Fill only backend/server-side secrets in `.env`; do not expose provider keys or repository tokens to browser-facing surfaces.
4. Start the stack with `scripts/dev/start-real-stack.bat` on Windows or `scripts/dev/start-real-stack.ps1` from PowerShell.
5. Open `http://127.0.0.1:3000` or the configured private URL.
6. Use the bootstrap/admin flow to initialize the first operator account.
7. Run readiness checks and archive evidence before claiming customer readiness.
8. For paid handoff, copy `templates/self-hosted-entitlement.example.json` into a private customer delivery record and fill the support boundary fields without adding secrets.

## Required Evidence Before Clean Handoff

- Package verifier JSON/Markdown.
- Pilot customer delivery kit verification JSON/Markdown.
- Clean self-hosted install rehearsal JSON/Markdown.
- OpenSpec strict validation.
- Governance guardrail summary.
- Canonical pre-release or explicitly accepted substitute.
- Release evidence JSON/Markdown.
- Hosted/operator readiness JSON/Markdown.
- Team workflow browser rehearsal when claiming multi-account readiness.
- Public GitHub import rehearsal before claiming live public-repo benchmark evidence.
- Readiness evidence history entry for durable customer claims.
- Team handoff report JSON/Markdown for customer or operator review.
- License/support boundary documentation and customer-specific entitlement record for paid handoff.

## Explicit Non-Goals

The package does not validate or include billing, full SaaS organization management, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, managed hosted operations, or runtime license enforcement.
