# Real External Host Trial Evidence

- Label: `customer-host-trial-isolated`
- Generated at: `2026-07-15T13:30:00+08:00`
- Status: `warning`
- Host proof level: `external_template_not_customer_controlled`
- Host input: `.tmp/customer-host-trial-input.json`
- Selected repositories: `-`
- Pass lanes: `7`
- Warning lanes: `8`
- Blocking lanes: `0`
- Placeholder findings: `0`
- Redaction findings: `0`

## Evidence Lanes

| Lane | Status | Source | Summary | Warnings |
| --- | --- | --- | --- | --- |
| Sanitized host input | warning | .tmp/customer-host-trial-input.json | {"browser_smoke_status": "pass", "commit": "b613033", "deployment_mode": "docker-compose", "host_class": "isolated-local-docker", "is_customer_controlled": false, "operator": "local-operator", "os_family": "Windows", "package_label": "decisionatlas-self-hosted", "required_finding_count": 1, "version_label": "customer-host-trial-2026-07-15"} | ["host_not_customer_controlled"] |
| Stack startup | pass | - | Managed real stack started successfully on the isolated host. | [] |
| Service health | pass | - | Web, API, and engine health checks returned healthy responses. | [] |
| Administrator login | pass | - | Local administrator bootstrap session reached the workspace UI without recording credentials. | [] |
| Team and workspace setup | operator_guided | - | Team control plane is reachable; reviewer/viewer account assignment remains a customer-operator step. | ["lane_not_clean"] |
| Repository import | pass | - | Fresh public GitHub repository hynek/structlog imported successfully with 1,169 objects and 26 candidates. | [] |
| Candidate review | pass | - | Review queue rendered 26 imported candidates in the real browser. | [] |
| Why search | warning | - | Why Search executed and failed closed with review_required and zero citations before accepted baseline creation. | ["lane_not_clean"] |
| Drift evaluation | warning | - | Drift evaluation completed with review_required and zero alerts because accepted baseline is empty. | ["lane_not_clean"] |
| Backup and recovery | operator_guided | - | Backup, restore, and upgrade rehearsal completed as operator-guided evidence on the isolated host. | ["lane_not_clean"] |
| Browser smoke | pass | - | Chrome verified home, team, settings, evidence, workspace dashboard, review, Why, timeline, and Drift routes. | [] |
| Placeholder/template review | pass | - | {"finding_count": 0, "finding_ids": []} | [] |
| Required host field review | warning | - | {"finding_count": 1, "finding_ids": ["host_not_customer_controlled"]} | ["host_not_customer_controlled"] |
| Customer-host v2 | not_provided | - | {"host_proof_level": "not_provided", "status": "not_provided"} | ["source_not_provided"] |
| Full-chain random repo release | warning | .tmp/customer-host-trial-fresh-repo.json | {"blocker_count": 0, "blocking": null, "limitations": ["A seeded bounded pool is random and reproducible but is not an unbounded sample of GitHub.", "GitHub and the real local stack are external runtime dependencies.", "A successful import can still yield evidence-limited decision quality.", "Evidence excludes credentials, raw private source, raw model output, and unbounded logs."], "not_provided": null, "operator_guided": null, "pass": null, "selected_repo_ids": [], "status": "warning", "warning": null} | [] |

## Placeholder Findings

- none

## Limitations

- This evidence validates sanitized operator-supplied facts; it does not embed raw customer logs or secrets.
- A clean pass requires real non-template external/customer-controlled host input and clean source evidence.
- Local smoke or example-template evidence remains useful for pipeline testing but is not customer proof.

## Recommended Next Actions

- Resolve or explicitly disclose non-clean trial lanes: host_input, team_workspace, why, drift, continuity, required_host_review, customer_host_v2, full_chain_random_repo_release.
- Archive this evidence into readiness history only after confirming the boundary is acceptable.

## Evidence Boundary

- Do not include tokens, .env files, private repository contents, raw database backups, raw model output, or raw customer logs in this evidence.
