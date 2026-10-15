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
    external-self-hosted-install-evidence.example.json
    customer-host-trial.example.json
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
      pilot-commercial-proposal-kit.md
      pilot-paid-quote-template.md
      pilot-acceptance-checklist.md
      pilot-support-renewal-upgrade-boundary.md
      self-hosted-operations-runbook.md
      team-handoff-reporting.md
      external-self-hosted-install-evidence.md
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
      collect_real_external_host_trial_evidence.py
      collect_team_handoff_report.py
      collect_external_self_hosted_install_evidence.py
      verify_pilot_customer_delivery_kit.py
      verify_pilot_commercial_proposal_kit.py
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

The verifier checks package structure and manifest integrity. It does not start Docker, validate live credentials, import private repositories, run a live benchmark, or prove installation on a customer-controlled host. Those remain separate rehearsal evidence.

Verify the pilot customer materials:

```powershell
python scripts\ci\verify_pilot_customer_delivery_kit.py `
  --output-json .tmp\pilot-customer-delivery-kit-verification.json `
  --output-markdown .tmp\pilot-customer-delivery-kit-verification.md
```

Verify the paid pilot commercial proposal materials:

```powershell
python scripts\ci\verify_pilot_commercial_proposal_kit.py `
  --output-json .tmp\pilot-commercial-proposal-kit-verification.json `
  --output-markdown .tmp\pilot-commercial-proposal-kit-verification.md
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
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json `
  --output-json .tmp\clean-self-hosted-install-rehearsal.json `
  --output-markdown .tmp\clean-self-hosted-install-rehearsal.md
```

The clean rehearsal copies the package into `.tmp/clean-self-hosted-install/<label>/package-copy`, checks operator handoff entry points, preserves missing or non-pass evidence states, and writes operator-readable Markdown. Package verification and local clean rehearsal are necessary but not sufficient for clean customer-host proof.

## Collect External Install Evidence

Use external install evidence when the package is exercised on a clean VM, another machine, or customer-controlled host:

```powershell
python scripts\ci\collect_external_self_hosted_install_evidence.py `
  --input-json templates\external-self-hosted-install-evidence.example.json `
  --output-json .tmp\external-self-hosted-install-evidence.json `
  --output-markdown .tmp\external-self-hosted-install-evidence.md
```

Fill the input file on the external host before running the collector. Missing evidence remains `not_provided` or `operator_guided`; blocked or unsafe evidence must not be treated as pass.

For the complete customer-host loop, copy `templates/customer-host-trial.example.json` to a private working file on the target host, fill only bounded statuses and summaries, and run:

```powershell
python scripts\ci\collect_real_external_host_trial_evidence.py `
  --label customer-host-trial-<date> `
  --version-label <package-version> `
  --commit <package-commit> `
  --host-input-json .\customer-host-trial.json `
  --customer-host-v2-json .\customer-host-v2.json `
  --full-chain-json .\full-chain-release.json `
  --output-json .tmp\real-external-host-trial-evidence.json `
  --output-markdown .tmp\real-external-host-trial-evidence.md `
  --archive-history `
  --archive-label customer-host-trial-<date>
```

The collector validates the submitted observations but does not install software, start services, import repositories, run browsers, or mutate the target host. A local workstation or local Docker rehearsal must remain `operator_guided`; only an independently controlled external host with clean core lanes can produce `real_external_customer_controlled` proof.

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
- Pilot commercial proposal kit verification JSON/Markdown when paid pilot outreach is part of the handoff.
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
- External self-hosted install evidence JSON/Markdown before claiming that the package was validated on a clean VM, another machine, or customer-controlled host.
- License/support boundary documentation and customer-specific entitlement record for paid handoff.

## Explicit Non-Goals

The package does not validate or include billing, full SaaS organization management, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, enterprise SSO, managed hosted operations, or runtime license enforcement.
