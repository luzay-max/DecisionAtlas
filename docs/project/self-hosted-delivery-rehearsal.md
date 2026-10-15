# Self-Hosted Delivery Rehearsal

[Home](../../README.md) | [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Package Guide](self-hosted-package-guide.md) | [Operations Runbook](self-hosted-operations-runbook.md) | [Continuity Rehearsal](backup-restore-upgrade-rehearsal.md) | [Code Decision Audit Template](code-decision-audit-template.md) | [Readiness Evidence History](../evidence/readiness/index.md)

---

Use this rehearsal before claiming a self-hosted deployment is ready for customer evaluation, a paid pilot, or an enterprise handoff. The rehearsal ties together startup, release evidence, hosted/operator readiness, benchmark comparison, readiness evidence history, and customer-readable handoff material.

This rehearsal validates the self-hosted/private-deployment path. It does not validate billing, hosted multi-tenancy, Marketplace or self-service OAuth, hosted secret vault, managed hosted service operations, or runtime license enforcement.

## Rehearsal Scope

Recommended label format:

```text
self-hosted-delivery-rehearsal
```

Recommended durable history entry:

```text
docs/evidence/readiness/YYYY-MM-DD-self-hosted-delivery-rehearsal/
```

Classify every lane explicitly:

| State | Meaning |
| --- | --- |
| `pass` / `passed` | Evidence supports the claim. |
| `warning` / `non_blocking` | Usable with disclosure or follow-up. |
| `blocking` | Do not claim readiness until resolved or excluded. |
| `operator_guided` | Operator action, URL, credential, provider, or manual decision is still required. |
| `known_limitation` | Current environment cannot validate the lane; rerun condition is known. |
| `not_provided` | Optional evidence was omitted and must not be treated as pass. |

## Required Evidence Families

| Evidence family | Required for rehearsal | Expected output |
| --- | --- | --- |
| Self-hosted package manifest | Yes for package handoff claims | `.tmp/self-hosted-package/<label>/manifest.json` |
| Self-hosted package verification | Yes for package handoff claims | `.tmp/self-hosted-package-verification.json` and Markdown |
| Clean self-hosted install rehearsal | Yes before external operator trial readiness claims | `.tmp/clean-self-hosted-install-rehearsal.json` and Markdown |
| External self-hosted install evidence | Required before customer-host install claims | `.tmp/external-self-hosted-install-evidence.json` and Markdown, or `not_provided` / `operator_guided` |
| OpenSpec strict validation | Yes | Command output recorded in handoff summary |
| Governance guardrail | Yes | `.tmp/agent-guardrail.json` and summary text |
| Canonical pre-release | Yes, or explicit blocker/substitute | `.tmp/pre-release-rehearsal-YYYY-MM-DD.log` and status |
| Release evidence | Yes | `.tmp/release-evidence.json` and `.tmp/release-evidence.md` |
| Hosted/operator readiness | Yes | `.tmp/hosted-operator-readiness.json` and `.tmp/hosted-operator-readiness.md` |
| Team workflow browser rehearsal | Yes for Team Self-hosted claims | Playwright output for `team-self-hosted-rehearsal.spec.ts` |
| Public GitHub import rehearsal | Required before claiming live public-repo benchmark evidence | `.tmp/public-github-import-rehearsal.json` and `.tmp/public-github-import-rehearsal.md` |
| Benchmark comparison | Optional credibility lane, but must be explicit | `.tmp/real-repo-benchmark-comparison.json` and Markdown, or `not_provided` |
| Readiness evidence history | Yes for durable claims | `docs/evidence/readiness/<entry>/entry.json` plus copied artifacts |
| Handoff summary | Yes | `docs/evidence/readiness/<entry>/summary.md` |
| Code Decision Audit sample | Required for paid pilot/customer evaluation | `docs/evidence/readiness/<entry>/code-decision-audit-sample.md` |
| Backup/restore/upgrade rehearsal | Required before clean long-term self-hosted continuity claims | `.tmp/backup-restore-upgrade-rehearsal.json` and Markdown |
| Real backup/restore/upgrade rehearsal | Required before claiming tested backup/restore/upgrade mechanics | `.tmp/real-backup-restore-upgrade-rehearsal.json` and Markdown, or `not_provided` / `operator_guided` |

## Execution Flow

1. Confirm the deployment mode and target URLs.
2. Start or verify the self-hosted stack. On Windows, prefer `scripts\dev\start-real-stack.bat` for one-click local startup.
3. Probe Web, API, and Engine health.
4. Build and verify the self-hosted package when claiming package handoff readiness.
5. Run OpenSpec strict validation.
6. Run governance guardrail summary and JSON output.
7. Run the canonical pre-release baseline, or record the exact blocker and accepted substitute evidence.
8. Run seeded demo readiness using the project Python environment when database dependencies are required.
9. Run the Team Self-hosted browser rehearsal when claiming small-team account/permission readiness.
10. Generate release evidence.
11. Generate hosted/operator readiness evidence.
12. Run public GitHub import rehearsal before claiming live public-repository benchmark evidence.
13. Generate, reuse, or explicitly omit benchmark comparison evidence.
14. Archive selected artifacts into readiness evidence history.
15. Prepare the rehearsal summary and Code Decision Audit handoff.
16. Generate backup/restore/upgrade rehearsal evidence before claiming long-term continuity readiness.
17. Collect external self-hosted install evidence before claiming a clean VM, another machine, or customer-controlled host passed the install flow.

## Command Template

```powershell
$Label = "self-hosted-delivery-rehearsal"
$Date = Get-Date -Format "yyyy-MM-dd"

openspec validate --all --strict
python scripts\ci\build_self_hosted_package.py --label decisionatlas-self-hosted --version-label "self-hosted-rehearsal-$Date"
python scripts\ci\verify_self_hosted_package.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --output-json .tmp\self-hosted-package-verification.json `
  --output-markdown .tmp\self-hosted-package-verification.md
python scripts\ci\rehearse_clean_self_hosted_install.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --package-verification-json .tmp\self-hosted-package-verification.json `
  --output-json .tmp\clean-self-hosted-install-rehearsal.json `
  --output-markdown .tmp\clean-self-hosted-install-rehearsal.md
python scripts\ci\rehearse_backup_restore_upgrade.py `
  --input-json templates\backup-restore-upgrade-rehearsal.example.json `
  --output-json .tmp\backup-restore-upgrade-rehearsal.json `
  --output-markdown .tmp\backup-restore-upgrade-rehearsal.md
python scripts\ci\rehearse_real_backup_restore_upgrade.py `
  --label real-continuity-rehearsal `
  --previous-version "self-hosted-rehearsal-before-$Date" `
  --target-version "self-hosted-rehearsal-$Date" `
  --output-json .tmp\real-backup-restore-upgrade-rehearsal.json `
  --output-markdown .tmp\real-backup-restore-upgrade-rehearsal.md
python scripts\ci\collect_external_self_hosted_install_evidence.py `
  --input-json templates\external-self-hosted-install-evidence.example.json `
  --output-json .tmp\external-self-hosted-install-evidence.json `
  --output-markdown .tmp\external-self-hosted-install-evidence.md
python scripts\governance\agent_guardrail.py --pretty > .tmp\agent-guardrail.json
python scripts\governance\agent_guardrail.py --summary > .tmp\agent-guardrail-summary.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1 *> ".tmp\pre-release-rehearsal-$Date.log"
python -m uv run --project services/engine python scripts\demo\check_seeded_demo.py --json --no-fail > .tmp\seeded-demo-readiness.json
pnpm --filter @decisionatlas/web e2e -- team-self-hosted-rehearsal.spec.ts
python scripts\ci\rehearse_public_github_import.py --repo-id fastapi --base-url http://127.0.0.1:3001 --wait

python scripts\ci\collect_release_evidence.py `
  --pre-release-status passed `
  --openspec-status passed `
  --offline-benchmark-status passed `
  --guardrail-report .tmp/agent-guardrail.json `
  --benchmark-comparison-report .tmp/real-repo-benchmark-comparison.json

python scripts\demo\collect_hosted_readiness.py `
  --web-status operator_guided `
  --api-status pass `
  --engine-status operator_guided `
  --health-status operator_guided `
  --smoke-status operator_guided `
  --seeded-readiness-report .tmp/seeded-demo-readiness.json `
  --recovery-status operator_guided `
  --guardrail-report .tmp/agent-guardrail.json `
  --release-evidence-report .tmp/release-evidence.json `
  --real-repo-evidence-report .tmp/real-repo-benchmark-comparison.json

python scripts\ci\collect_readiness_evidence_history.py archive `
  --label $Label `
  --version-label "self-hosted-rehearsal-$Date" `
  --commit <commit> `
  --release-evidence-json .tmp/release-evidence.json `
  --release-evidence-markdown .tmp/release-evidence.md `
  --hosted-readiness-json .tmp/hosted-operator-readiness.json `
  --hosted-readiness-markdown .tmp/hosted-operator-readiness.md `
  --benchmark-comparison-json .tmp/real-repo-benchmark-comparison.json `
  --benchmark-comparison-markdown .tmp/real-repo-benchmark-comparison.md `
  --external-install-evidence-json .tmp/external-self-hosted-install-evidence.json `
  --external-install-evidence-markdown .tmp/external-self-hosted-install-evidence.md `
  --real-continuity-rehearsal-json .tmp/real-backup-restore-upgrade-rehearsal.json `
  --real-continuity-rehearsal-markdown .tmp/real-backup-restore-upgrade-rehearsal.md `
  --team-handoff-json .tmp/team-handoff-report.json `
  --team-handoff-markdown .tmp/team-handoff-report.md `
  --code-decision-audit-json .tmp/code-decision-audit-report.json `
  --code-decision-audit-markdown .tmp/code-decision-audit-report.md
```

If Web, API, Engine, hosted URLs, provider credentials, private repository credentials, or live benchmark inputs are absent, record the lane as `operator_guided`, `known_limitation`, `not_provided`, or `blocking`. Do not convert it into pass.

## Clean Install Rehearsal

Clean install rehearsal is the bridge between package structure verification and customer/operator trial readiness. It copies the package into `.tmp/clean-self-hosted-install/<label>/package-copy`, verifies package handoff entry points, ingests available release/readiness/benchmark/history/package/handoff evidence, and emits `.tmp/clean-self-hosted-install-rehearsal.json/md`.

Use the report as a bounded statement:

- `pass` means the supplied package copy and evidence inputs are clean for this rehearsal.
- `warning` means package structure may be usable but evidence is missing, operator-guided, known-limited, or non-clean.
- `blocking` means a required package asset, package input, or hard evidence input must be fixed before external operator trial.

Do not claim a clean external operator trial if this evidence is missing. Do not claim customer-host install proof unless external self-hosted install evidence is supplied and blocking lanes are clear.

## External Install Evidence

External install evidence records what happened on a clean VM, another machine, or customer-controlled host. It is generated from an explicit operator-filled JSON file and does not synthesize pass evidence from the local developer machine.

Use it when customer-facing material needs to say the package was tried outside the development workstation:

```powershell
python scripts\ci\collect_external_self_hosted_install_evidence.py `
  --input-json templates\external-self-hosted-install-evidence.example.json `
  --output-json .tmp\external-self-hosted-install-evidence.json `
  --output-markdown .tmp\external-self-hosted-install-evidence.md
```

Attach the resulting JSON to clean install rehearsal, team handoff, and Code Decision Audit reports. If it is absent, preserve `not_provided` or `operator_guided` instead of describing local clean rehearsal as external proof.

## Customer Host Trial Checklist

Use `templates/customer-host-trial.example.json` as the bounded input contract. Fill it on the target host or in a private operator workspace; do not commit the filled file.

1. Record the host class, OS family, deployment mode, operator, package version, and commit. Mark whether the host is independently customer-controlled.
2. Verify the package manifest and run `scripts/dev/start-real-stack.bat` on Windows or `scripts/dev/start-real-stack.ps1` on Linux/PowerShell.
3. Run Web, API, and Engine health checks. Record only pass/warning/blocking status and a short sanitized summary.
4. Initialize the first administrator, create reviewer/viewer accounts, and verify workspace permission boundaries without recording credentials.
5. Import one permitted fresh public GitHub repository or one approved private repository. Record repo identity and bounded import status only.
6. Open the dashboard, review queue, Why Search, Drift, and Evidence pages in a browser. Record route/status results, not screenshots containing secrets or private source.
7. Run the approved backup/recovery check and record whether recovery was validated, operator-guided, or not provided.
8. Review the completed input for tokens, `.env` values, private keys, raw logs, private source, raw model output, and backup contents.
9. Generate and archive the trial evidence:

```powershell
python scripts\ci\collect_real_external_host_trial_evidence.py `
  --label customer-host-trial-<date> `
  --version-label <package-version> `
  --commit <package-commit> `
  --host-input-json .\customer-host-trial.json `
  --output-json .tmp\real-external-host-trial-evidence.json `
  --output-markdown .tmp\real-external-host-trial-evidence.md `
  --archive-history `
  --archive-label customer-host-trial-<date>
```

The collector does not execute the checklist. It validates and summarizes operator-supplied facts. Local Docker or developer-workstation results remain `operator_guided`; do not use them as customer-host proof.

## Real Continuity Rehearsal

The non-destructive backup/restore/upgrade verifier checks operator-submitted evidence. The real continuity rehearsal checks mechanics against isolated scratch state:

```powershell
python scripts\ci\rehearse_real_backup_restore_upgrade.py `
  --label real-continuity-rehearsal `
  --previous-version <previous> `
  --target-version <target> `
  --output-json .tmp\real-backup-restore-upgrade-rehearsal.json `
  --output-markdown .tmp\real-backup-restore-upgrade-rehearsal.md
```

Use its JSON in handoff and audit reports before claiming tested backup/restore/upgrade readiness. If it is absent, keep continuity mechanics as `not_provided` or `operator_guided`.

## Public GitHub Import Rehearsal

The public GitHub import rehearsal is the setup proof for optional live benchmark claims. It checks whether the curated public repository workspace already exists, imports it through the normal public GitHub import path when missing, and writes JSON/Markdown evidence describing whether the workspace was created, reused, or remains blocked by operator setup, provider/network failure, or local-stack failure.

Use this command before running live benchmark validation for `fastapi/fastapi`:

```powershell
python scripts\ci\rehearse_public_github_import.py `
  --repo-id fastapi `
  --base-url http://127.0.0.1:3001 `
  --wait `
  --output-json .tmp\public-github-import-rehearsal.json `
  --output-markdown .tmp\public-github-import-rehearsal.md
```

Only treat subsequent live benchmark output as product evidence when the import rehearsal reports `benchmark_ready: true`. If the rehearsal reports `missing_workspace`, `operator_guided`, `provider_failure`, or `local_stack_failure`, keep the benchmark lane non-pass and preserve the limitation in release evidence.

## Team Self-Hosted Browser Rehearsal

The team browser rehearsal is the product-level proof for the small-team collaboration claim. It uses the local bootstrap admin to open the team management surface, creates reviewer and viewer accounts through the UI, logs in as those non-admin users, and verifies the product explains that admin role is required for account and workspace-permission management.

Use backend role-boundary tests as the authorization proof:

```powershell
python -m uv run pytest tests/api/test_team_api.py tests/api/test_auth_api.py -q
```

Use the browser rehearsal as the human-operator proof:

```powershell
pnpm --filter @decisionatlas/web e2e -- team-self-hosted-rehearsal.spec.ts
```

If this browser rehearsal is skipped, do not claim clean Team Self-hosted account/permission readiness. Mark the lane as `not_provided` or `operator_guided` and explain what was not exercised.

## Multi Git Source Setup Boundary

The repository access setup surface is provider-aware for self-hosted operators:

- GitHub token setup is implemented and delegates to the existing owner-scoped private access binding path.
- GitHub public setup can reuse the existing repository lookup path.
- GitLab and Gitee setup are recognized but currently return a bounded `provider_unsupported` outcome with `plan_provider_importer` as the next action.
- Local path setup is recognized but currently returns `local_path_unavailable` / `operator_guided`; raw local paths must not be rendered into readiness evidence or non-admin surfaces.
- Token material remains write-only: setup responses, UI state, release evidence, and logs intended for readiness history must not echo submitted tokens.

Use this boundary when explaining customer readiness. Do not claim full GitLab, Gitee, or local filesystem ingestion until provider-specific importers are implemented and rehearsed.

## Handoff Rules

- Customer-facing claims must reference the readiness history entry or state that rehearsal evidence is missing.
- `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states must remain visible in the summary.
- `.tmp` output remains scratch evidence unless explicitly copied into readiness evidence history.
- Complete delivery rehearsal history should include release, hosted, benchmark, external install, real continuity, handoff, and audit evidence when those claims are part of the handoff.
- Do not archive secrets, private repository contents, raw model output, or unnecessary local-only logs.
- For paid pilots, prepare a Code Decision Audit report from the generated evidence.
