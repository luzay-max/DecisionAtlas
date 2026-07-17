# Self-Hosted Release Package Guide

[Home](../../README.md) | [Deployment](deployment.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Delivery Rehearsal](self-hosted-delivery-rehearsal.md) | [Operations Runbook](self-hosted-operations-runbook.md)

---

Use this guide when preparing a DecisionAtlas package for a private server, paid pilot, or small-team self-hosted evaluation.

The package is a runnable source-tree handoff bundle, not a binary installer. It contains the pinned Node/Python workspace inputs, web/API/engine runtime source, migrations, prompts, Compose support, bounded smoke assets, operator docs, environment templates, and a machine-readable manifest. It does not include customer secrets, databases, imported repositories, node modules, virtual environments, browser binaries, dependency caches, or local scratch output.

For external evaluation, start with [Pilot Customer Delivery Kit](pilot-customer-delivery-kit.md). It provides the one-page product explanation, demo script, deployment checklist, FAQ, tier comparison, and delivery email template that should accompany the technical package.

## Package Layout

Expected layout:

```text
decisionatlas-self-hosted/
  manifest.json
  README.md
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
  docker-compose.yml
  apps/
    api/
    web/
  services/
    engine/
  packages/
    prompts/
  infra/
    docker/
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
      rehearse_runnable_self_hosted_package.py
      start-engine-smoke.ps1
      start-api-smoke.ps1
      start-web-smoke.ps1
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

## Publish Versioned Release Artifacts

After the package directory passes verification, create portable release files:

```powershell
python scripts\ci\publish_self_hosted_release_artifacts.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --output-root .tmp\self-hosted-release-artifacts `
  --output-json .tmp\self-hosted-release-publication.json `
  --output-markdown .tmp\self-hosted-release-publication.md
```

The version label in `manifest.json` becomes the release directory and archive suffix. The output contains:

```text
<version>/
  decisionatlas-self-hosted-<version>.zip
  decisionatlas-self-hosted-<version>.tar.gz
  decisionatlas-self-hosted-<version>.cdx.json
  release-artifacts.json
  SHA256SUMS
```

ZIP and tar.gz contain the same files under one `decisionatlas-self-hosted-<version>/` root. `SOURCE_DATE_EPOCH` or `--source-date-epoch` controls normalized archive timestamps for repeatable builds.

Verify checksums, archive safety, member parity, SBOM structure, and both extracted package copies before unpacking for normal use:

```powershell
python scripts\ci\verify_self_hosted_release_artifacts.py `
  --release-dir .tmp\self-hosted-release-artifacts\<version> `
  --extract-verified-to C:\DecisionAtlas\verified-<version> `
  --output-json .tmp\self-hosted-release-artifact-verification.json `
  --output-markdown .tmp\self-hosted-release-artifact-verification.md
```

The `--extract-verified-to` destination must be empty or absent. The verifier writes the retained ZIP extraction only after every checksum, archive, SBOM, parity, and package check passes, then verifies the retained package again.

Do not use `Expand-Archive`, `tar -xf`, or a GUI extractor on an unverified bundle. The verifier rejects absolute paths, traversal, backslashes, duplicate members, symlinks, special files, unexpected roots, forbidden secret/cache paths, checksum mismatches, and ZIP/tar member differences before extraction.

`SHA256SUMS` proves integrity relative to a trusted manifest source; it does not authenticate the publisher. Cryptographic signing is not included yet. The CycloneDX SBOM covers locked Node and Python dependencies, not OS packages, container images, runtime plugins, or vulnerability analysis. Archives also exclude dependency caches, so install still requires network access or an approved operator-supplied cache.

## Verify Package

Run the offline package verifier:

```powershell
python scripts\ci\verify_self_hosted_package.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --output-json .tmp\self-hosted-package-verification.json `
  --output-markdown .tmp\self-hosted-package-verification.md
```

The verifier checks package structure, runtime inventory, manifest integrity, and secret/cache exclusion. A legacy structure-only package remains readable but fails the runnable package claim. The verifier does not start services, validate live credentials, import private repositories, or prove installation on a customer-controlled host. Those remain separate rehearsal evidence.

## Install And Run From The Package Copy

The package requires Node.js, pnpm, Python, uv, Docker Desktop or equivalent PostgreSQL/Redis services, and network access to package registries unless the operator supplies an approved dependency cache.

For restricted-network installation, use [Offline Dependency Bundle Guide](offline-dependency-bundle-guide.md). The online preparation step creates a separate package-bound bundle for pnpm, uv, Playwright Chromium, and the allowlisted Compose images. Verify both the source package and bundle before transfer; do not merge global developer caches into the delivery.

From the package root:

```powershell
pnpm install --frozen-lockfile
uv sync --project services/engine --frozen
Copy-Item templates\self-hosted.env.example .env
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

The startup script uses the fixed Compose project name `decisionatlas`, so a renamed package directory does not create conflicting PostgreSQL or Redis container identities.

Run the bounded isolated-copy rehearsal from the maintainer or independent runner checkout:

```powershell
python scripts\ci\rehearse_runnable_self_hosted_package.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --host-class independent-runner `
  --os-family windows `
  --repo githits-com/githits-cli `
  --install-dependencies `
  --install-browser `
  --run-smoke `
  --output-json .tmp\runnable-self-hosted-package-rehearsal.json `
  --output-markdown .tmp\runnable-self-hosted-package-rehearsal.md
```

The rehearsal copies the package outside the source checkout, verifies that copy, installs exact dependencies there, starts Engine/API/Web through Playwright health gates, and exercises an imported-workspace browser loop. A passing local isolated copy or GitHub-hosted runner proves package independence. It does not become customer-controlled-host proof unless a separate sanitized external trial says `is_customer_controlled=true`.

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
  --runnable-package-rehearsal-json .tmp\runnable-self-hosted-package-rehearsal.json `
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
- Runnable package rehearsal JSON/Markdown from a package copy outside the maintainer checkout.
- Versioned ZIP/tar.gz publication report, `SHA256SUMS`, CycloneDX SBOM, and release-artifact verification JSON/Markdown.
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
