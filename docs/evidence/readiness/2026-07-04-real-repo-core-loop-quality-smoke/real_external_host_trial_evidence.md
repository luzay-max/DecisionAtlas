# Real External Host Trial Evidence

- Label: `2026-07-04-real-repo-core-loop-quality-smoke`
- Generated at: `2026-07-04T00:16:00+00:00`
- Status: `warning`
- Host proof level: `template_or_placeholder`
- Host input: `templates/external-customer-host-rehearsal-v2.example.json`
- Selected repositories: `n8n, rich`
- Pass lanes: `2`
- Warning lanes: `3`
- Blocking lanes: `0`
- Placeholder findings: `8`
- Redaction findings: `0`

## Evidence Lanes

| Lane | Status | Source | Summary | Warnings |
| --- | --- | --- | --- | --- |
| Sanitized host input | pass | templates/external-customer-host-rehearsal-v2.example.json | {"browser_smoke_status": "pass", "commit": "fill-me", "deployment_mode": "docker-compose", "host_class": "customer-vm", "is_customer_controlled": true, "operator": "customer-or-operator-name", "os_family": "Windows Server or Linux", "package_label": "decisionatlas-self-hosted", "required_finding_count": 0, "version_label": "fill-me"} | [] |
| Placeholder/template review | warning | - | {"finding_count": 8, "finding_ids": ["fill_me", "customer_or_operator_name", "fill_me", "fill_me", "optional_placeholder", "customer_or_operator_name", "customer_or_operator_name", "replace_sample"]} | ["fill_me", "customer_or_operator_name", "fill_me", "fill_me", "optional_placeholder", "customer_or_operator_name", "customer_or_operator_name", "replace_sample"] |
| Required host field review | pass | - | {"finding_count": 0, "finding_ids": []} | [] |
| Customer-host v2 | warning | .tmp/external-customer-host-rehearsal-v2.json | {"blocker_count": 0, "blocking": 0, "host_proof_level": "customer_controlled_with_browser_smoke", "limitations": ["Replace this sample with real customer-host observations before handoff.", "Do not paste secrets, raw logs, private source, .env values, or database backups into this file."], "not_provided": 0, "operator_guided": 0, "pass": 3, "status": "warning", "warning": 4} | [] |
| Full-chain random repo release | warning | .tmp/full-chain-random-repo-release-rehearsal.json | {"blocker_count": 0, "blocking": 0, "limitations": ["This bundle composes bounded evidence; it does not embed raw logs, secrets, or private repository content.", "Random real repository diagnosis depends on local stack, GitHub, and provider availability.", "Customer-host proof is only as strong as the supplied customer-host v2 evidence."], "not_provided": 0, "operator_guided": 0, "pass": 1, "selected_repo_ids": ["n8n", "rich"], "status": "warning", "warning": 4} | [] |

## Placeholder Findings

- `fill_me` at `$.host_profile.os_version`
- `customer_or_operator_name` at `$.host_profile.operator`
- `fill_me` at `$.package_identity.version_label`
- `fill_me` at `$.package_identity.commit`
- `optional_placeholder` at `$.package_identity.package_manifest_sha256`
- `customer_or_operator_name` at `$.browser_smoke.operator`
- `customer_or_operator_name` at `$.redaction_acknowledgement.reviewer`
- `replace_sample` at `$.limitations[0]`

## Limitations

- This evidence validates sanitized operator-supplied facts; it does not embed raw customer logs or secrets.
- A clean pass requires real non-template external/customer-controlled host input and clean source evidence.
- Local smoke or example-template evidence remains useful for pipeline testing but is not customer proof.

## Recommended Next Actions

- Replace example/template placeholder values with real sanitized external host observations.
- Resolve or explicitly disclose non-clean trial lanes: placeholder_review, customer_host_v2, full_chain_random_repo_release.
- Archive this evidence into readiness history only after confirming the boundary is acceptable.

## Evidence Boundary

- Do not include tokens, .env files, private repository contents, raw database backups, raw model output, or raw customer logs in this evidence.
