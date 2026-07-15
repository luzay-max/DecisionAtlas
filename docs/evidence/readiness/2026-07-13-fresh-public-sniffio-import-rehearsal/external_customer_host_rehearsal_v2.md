# External Customer Host Rehearsal v2

- Label: `full-chain-customer-host-v2-source`
- Generated at: `2026-07-03T06:35:10.721131+00:00`
- Status: `warning`
- Host proof level: `customer_controlled_with_browser_smoke`
- Host input: `templates/external-customer-host-rehearsal-v2.example.json`
- Pass lanes: `3`
- Warning lanes: `4`
- Blocking lanes: `0`
- Operator-guided lanes: `0`
- Not-provided lanes: `0`

## Host Profile

`{"deployment_mode": "docker-compose", "host_class": "customer-vm", "is_customer_controlled": true, "operator": "customer-or-operator-name", "os_family": "Windows Server or Linux", "os_version": "fill-me"}`

## Evidence Lanes

| Lane | Status | Source | Summary | Warnings |
| --- | --- | --- | --- | --- |
| Customer host template | pass | templates/external-customer-host-rehearsal-v2.example.json | {"deployment_mode": "docker-compose", "host_class": "customer-vm", "is_customer_controlled": true, "operator": "customer-or-operator-name", "os_family": "Windows Server or Linux", "redaction_acknowledged": true} | [] |
| Package verification | pass | .tmp/self-hosted-package-verification.json | {"commit": "bd481c85b88adf3cf41d9f9473dae651b3f70780", "generated_at": "2026-06-08T07:49:34.497822+00:00", "package_label": "decisionatlas-self-hosted", "package_path": "C:/Users/Max/Desktop/DecisionAtlas/.tmp/self-hosted-package/decisionatlas-self-hosted", "status": "pass", "version_label": "self-hosted-preview-2026-06-08"} | [] |
| Clean install rehearsal | warning | .tmp/clean-self-hosted-install-rehearsal.json | {"commit": "c00f65e", "generated_at": "2026-06-09T01:24:45.954699+00:00", "label": "clean-self-hosted-install-2026-06-09", "package_path": ".tmp/self-hosted-package/decisionatlas-self-hosted", "status": "warning", "version_label": "clean-self-hosted-install-2026-06-09"} | [] |
| External install evidence | warning | .tmp/external-self-hosted-install-evidence.json | {"generated_at": "2026-07-02T05:46:56.429683+00:00", "label": "external-self-hosted-install-example", "status": "warning"} | [] |
| Browser smoke | pass | - | {"operator": "customer-or-operator-name", "pages": ["/", "/team", "/review?workspace=demo-workspace", "/evidence"], "summary": "Opened home, team, review, evidence, and workspace pages."} | [] |
| Release rehearsal bundle | warning | .tmp/release-rehearsal-evidence.json | {"evidence_type": "release-rehearsal-one-command-evidence", "generated_at": "2026-07-03T06:34:41.379789+00:00", "label": "full-chain-random-repo-release-source", "status": "warning", "summary": {"blocking": 0, "missing_lanes": 0, "operator_guided_lanes": 1, "pass": 2, "warning": 5}} | [] |
| Readiness history | unknown | docs/evidence/readiness/index.json | {"generated_at": "2026-07-03T06:27:54.450965+00:00"} | [] |

## Limitations

- Replace this sample with real customer-host observations before handoff.
- Do not paste secrets, raw logs, private source, .env values, or database backups into this file.

## Recommended Next Actions

- Rerun or explicitly disclose non-pass customer-host lanes: clean_install, external_install, release_rehearsal, readiness_history.
- Archive customer-host v2 evidence into readiness history before customer handoff.

## Evidence Boundary

- Do not include tokens, .env files, private repository contents, raw database backups, or raw customer logs in this evidence.
