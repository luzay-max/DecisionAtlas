# Self-Hosted Delivery Rehearsal

[Home](../../README.md) | [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) | [Self-Hosted Readiness](self-hosted-readiness-checklist.md) | [Code Decision Audit Template](code-decision-audit-template.md) | [Readiness Evidence History](../evidence/readiness/index.md)

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
| OpenSpec strict validation | Yes | Command output recorded in handoff summary |
| Governance guardrail | Yes | `.tmp/agent-guardrail.json` and summary text |
| Canonical pre-release | Yes, or explicit blocker/substitute | `.tmp/pre-release-rehearsal-YYYY-MM-DD.log` and status |
| Release evidence | Yes | `.tmp/release-evidence.json` and `.tmp/release-evidence.md` |
| Hosted/operator readiness | Yes | `.tmp/hosted-operator-readiness.json` and `.tmp/hosted-operator-readiness.md` |
| Benchmark comparison | Optional credibility lane, but must be explicit | `.tmp/real-repo-benchmark-comparison.json` and Markdown, or `not_provided` |
| Readiness evidence history | Yes for durable claims | `docs/evidence/readiness/<entry>/entry.json` plus copied artifacts |
| Handoff summary | Yes | `docs/evidence/readiness/<entry>/summary.md` |
| Code Decision Audit sample | Required for paid pilot/customer evaluation | `docs/evidence/readiness/<entry>/code-decision-audit-sample.md` |

## Execution Flow

1. Confirm the deployment mode and target URLs.
2. Start or verify the self-hosted stack. On Windows, prefer `scripts\dev\start-real-stack.bat` for one-click local startup.
3. Probe Web, API, and Engine health.
4. Run OpenSpec strict validation.
5. Run governance guardrail summary and JSON output.
6. Run the canonical pre-release baseline, or record the exact blocker and accepted substitute evidence.
7. Run seeded demo readiness using the project Python environment when database dependencies are required.
8. Generate release evidence.
9. Generate hosted/operator readiness evidence.
10. Generate, reuse, or explicitly omit benchmark comparison evidence.
11. Archive selected artifacts into readiness evidence history.
12. Prepare the rehearsal summary and Code Decision Audit handoff.

## Command Template

```powershell
$Label = "self-hosted-delivery-rehearsal"
$Date = Get-Date -Format "yyyy-MM-dd"

openspec validate --all --strict
python scripts\governance\agent_guardrail.py --pretty > .tmp\agent-guardrail.json
python scripts\governance\agent_guardrail.py --summary > .tmp\agent-guardrail-summary.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1 *> ".tmp\pre-release-rehearsal-$Date.log"
python -m uv run --project services/engine python scripts\demo\check_seeded_demo.py --json --no-fail > .tmp\seeded-demo-readiness.json

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
  --benchmark-comparison-markdown .tmp/real-repo-benchmark-comparison.md
```

If Web, API, Engine, hosted URLs, provider credentials, private repository credentials, or live benchmark inputs are absent, record the lane as `operator_guided`, `known_limitation`, `not_provided`, or `blocking`. Do not convert it into pass.

## Handoff Rules

- Customer-facing claims must reference the readiness history entry or state that rehearsal evidence is missing.
- `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states must remain visible in the summary.
- `.tmp` output remains scratch evidence unless explicitly copied into readiness evidence history.
- Do not archive secrets, private repository contents, raw model output, or unnecessary local-only logs.
- For paid pilots, prepare a Code Decision Audit report from the generated evidence.
