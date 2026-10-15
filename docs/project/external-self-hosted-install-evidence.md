# External Self-Hosted Install Evidence

[Home](../../README.md) | [Self-Hosted Package](self-hosted-package-guide.md) | [Delivery Rehearsal](self-hosted-delivery-rehearsal.md) | [Team Handoff](team-handoff-reporting.md) | [Code Decision Audit](code-decision-audit-template.md)

---

Use this evidence when claiming that a DecisionAtlas self-hosted package was exercised outside the developer workstation: a clean VM, another machine, or a customer-controlled host.

Local package verification and local clean install rehearsal are still required, but they are not customer-host proof. External install evidence is the separate layer that records what happened on the outside host.

## Evidence Boundary

Allowed:

- Host class, OS, runtime, and whether the host is customer-controlled.
- Package label, version label, commit, and manifest checksum.
- Bounded lane summaries for startup, health checks, browser smoke, repository import, readiness evidence, and redaction review.
- Paths or filenames for generated evidence, if they do not expose private local paths or secrets.
- Limitations and rerun conditions.

Forbidden:

- Raw `.env` files or secret assignments.
- Provider keys, repository tokens, passwords, private keys, or database URLs.
- Raw database backups, dumps, or restore payloads.
- Raw private repository files, snippets, issue text, PR bodies, screenshots containing private code, or local customer paths.

## Operator Flow

1. Deploy or copy the self-hosted package to a clean VM, another machine, or customer-controlled host.
2. Copy `templates/external-self-hosted-install-evidence.example.json` to a private working file.
3. Fill host profile and package identity from that host.
4. Run startup, health, browser smoke, and repository import checks on that host.
5. Set each lane to `passed`, `warning`, `operator_guided`, `not_provided`, or `blocked`.
6. Remove raw secrets, raw private repository content, raw backups, and unbounded local-only paths.
7. Run the collector from the repository or package root:

```powershell
python scripts\ci\collect_external_self_hosted_install_evidence.py `
  --input-json templates\external-self-hosted-install-evidence.example.json `
  --output-json .tmp\external-self-hosted-install-evidence.json `
  --output-markdown .tmp\external-self-hosted-install-evidence.md
```

The collector reads only the explicit input JSON. It does not inspect local Docker state, local services, or developer machine files to synthesize pass evidence.

## Lane Semantics

| Lane | Expected evidence |
| --- | --- |
| `package_identity` | Package label, version, commit, and manifest checksum were recorded. |
| `startup` | Operator started the stack on the external host or recorded the blocker. |
| `health` | Web/API/Engine health was checked or explicitly deferred. |
| `browser_smoke` | Human or browser smoke confirmed the UI flow, or the missing check is disclosed. |
| `repository_import` | Public repository import ran, or private/public import was explicitly operator-guided. |
| `readiness_evidence` | Release evidence, hosted readiness, benchmark comparison, and handoff paths were attached or disclosed as missing. |
| `redaction_review` | Operator confirms no raw secrets, backups, or private source content are present. |

`blocked` means do not claim customer-host readiness. `warning`, `operator_guided`, and `not_provided` may be acceptable for an early pilot only if disclosed in the handoff and audit report.

## Downstream Use

Pass the generated JSON to downstream reports:

```powershell
python scripts\ci\collect_team_handoff_report.py `
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json

python scripts\ci\collect_code_decision_audit_report.py `
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json
```

When running clean install rehearsal, attach it as a separate evidence source:

```powershell
python scripts\ci\rehearse_clean_self_hosted_install.py `
  --package .tmp\self-hosted-package\decisionatlas-self-hosted `
  --external-install-evidence-json .tmp\external-self-hosted-install-evidence.json
```

## Customer-Facing Rule

Do not say "customer-host install passed" unless external install evidence exists and its blocking lanes are clear. If the evidence is missing, say:

```text
Local package verification and local clean install rehearsal passed or were run separately.
External/customer-host install evidence is not_provided or operator_guided.
```
