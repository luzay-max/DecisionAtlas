# Private Repo Pilot Evidence Template

[Home](../../README.md) | [Pilot Delivery Kit](pilot-customer-delivery-kit.md) | [Self-Hosted Commercial Baseline](self-hosted-commercial-baseline.md) | [Team Handoff](team-handoff-reporting.md) | [Code Decision Audit Template](code-decision-audit-template.md)

---

Use this template when a Team Self-hosted or Enterprise Self-hosted pilot needs to prove DecisionAtlas value against a private repository without exposing customer-controlled secrets or private source material.

This document defines the shareable evidence shape. It does not prove that a private repository was actually evaluated until an operator attaches a sanitized evidence file generated in the customer-controlled environment.

## Safety Boundary

Shareable private-repo pilot evidence must not include:

- repository access tokens
- token values
- provider API keys
- `.env` values
- raw private source content
- raw private source code
- raw private issue or pull-request text
- raw model output
- unredacted customer names, repository names, branch names, commit SHAs, user names, local paths, or screenshots containing private code

Allowed evidence is category-level and count-based:

- repository identity state such as `redacted`, `customer_controlled`, or `category_only`
- provider and access mode labels such as `github` and `token`
- setup status such as `operator_guided`, `pass`, `warning`, or `blocking`
- counts for imported artifacts, candidate decisions, accepted decisions, review actions, why-search checks, and drift checks
- high-level limitation categories and recommended next actions
- paths to locally retained evidence that remain on the customer-controlled host

## Required JSON Shape

Use `templates/private-repo-pilot-evidence.example.json` as the committed safe sample. A real private-repo run may copy that file locally and fill the fields with redacted values.

Required top-level fields:

| Field | Purpose |
| --- | --- |
| `schema_version` | Evidence schema version. |
| `generated_at` | Timestamp for this evidence. |
| `status` | Overall state: `pass`, `warning`, `blocking`, `operator_guided`, or `not_provided`. |
| `evidence_type` | Must identify private-repo pilot evidence. |
| `repository` | Redacted repository identity and provider/access labels. |
| `credential_custody` | Token/key handling declaration. |
| `redaction` | Source/content/customer redaction declaration. |
| `workflow_lanes` | Token setup, access validation, import, review, why-search, drift, and handoff states. |
| `metrics` | Count-only pilot outcomes. |
| `limitations` | Known limitations and missing evidence. |
| `recommended_next_actions` | Next operator or customer actions. |
| `operator_review` | Human review statement before sharing. |

## Required Workflow Lanes

Every private-repo pilot evidence file should include these lanes:

| Lane | Meaning |
| --- | --- |
| `token_setup` | Whether an admin/operator configured a least-privilege token or installation path. |
| `access_validation` | Whether repository lookup and access validation succeeded. |
| `import_run` | Whether import ran and how it ended. |
| `decision_review` | Whether candidate decisions were reviewed. |
| `why_search` | Whether why-search produced grounded answers or failed closed. |
| `drift_review` | Whether drift checks were useful, noisy, or not yet run. |
| `handoff_evidence` | Whether release/readiness/handoff/audit evidence was generated. |

Use `operator_guided` when a step must be completed locally and cannot be proven by committed sample evidence.

## Verification

Run the verifier before sharing or archiving sanitized evidence:

```powershell
python scripts\ci\verify_private_repo_pilot_evidence.py `
  --evidence-json templates\private-repo-pilot-evidence.example.json `
  --evidence-markdown docs\project\private-repo-pilot-evidence-example.md `
  --output-json .tmp\private-repo-pilot-evidence-verification.json `
  --output-markdown .tmp\private-repo-pilot-evidence-verification.md
```

The verifier checks the evidence shape, required statements, workflow lanes, non-pass preservation, and obvious token/secret patterns. It does not replace human review.

## Sharing Rule

Before sending private-repo pilot evidence to a customer or using it in a Code Decision Audit:

- confirm that the customer approved the redacted summary for sharing
- confirm that no token/key/source/private issue text is included
- preserve `warning`, `blocking`, `operator_guided`, `known_limitation`, and `not_provided` states
- keep full raw evidence on the customer-controlled host unless a separate agreement allows transfer

Do not describe template readiness as private-repo proof. Template readiness means the project can capture evidence safely; private-repo proof requires a completed customer-controlled run.
