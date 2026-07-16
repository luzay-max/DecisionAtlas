# Clean Self-Hosted Install Rehearsal

- Label: `clean-runnable-package-20260716`
- Generated at: `2026-07-16T08:09:03.103776+00:00`
- Version: `2026-07-16-preview`
- Commit: `working-tree`
- Package: `.tmp/self-hosted-packages/runnable-preview-20260716`
- Clean workspace: `.tmp/clean-self-hosted-install/clean-runnable-package-20260716`
- Clean package: `.tmp/clean-self-hosted-install/clean-runnable-package-20260716/package-copy`
- Status: `warning`

## Clean Workspace Checks

| Check | Status | Details |
| --- | --- | --- |
| Package copied into isolated clean workspace | pass | {"path": "<workspace>/.tmp/clean-self-hosted-install/clean-runnable-package-20260716/package-copy"} |
| Required handoff asset manifest.json | pass | {"path": "manifest.json"} |
| Required handoff asset README.md | pass | {"path": "README.md"} |
| Required handoff asset templates/self-hosted.env.example | pass | {"path": "templates/self-hosted.env.example"} |
| Required handoff asset templates/self-hosted-entitlement.example.json | pass | {"path": "templates/self-hosted-entitlement.example.json"} |
| Required handoff asset docs/project/self-hosted-package-guide.md | pass | {"path": "docs/project/self-hosted-package-guide.md"} |
| Required handoff asset docs/project/self-hosted-operations-runbook.md | pass | {"path": "docs/project/self-hosted-operations-runbook.md"} |
| Required handoff asset docs/project/self-hosted-readiness-checklist.md | pass | {"path": "docs/project/self-hosted-readiness-checklist.md"} |
| Required handoff asset docs/project/self-hosted-delivery-rehearsal.md | pass | {"path": "docs/project/self-hosted-delivery-rehearsal.md"} |
| Required handoff asset docs/project/self-hosted-license-and-support-boundary.md | pass | {"path": "docs/project/self-hosted-license-and-support-boundary.md"} |
| Required handoff asset docs/project/team-handoff-reporting.md | pass | {"path": "docs/project/team-handoff-reporting.md"} |
| Required handoff asset scripts/dev/start-real-stack.ps1 | pass | {"path": "scripts/dev/start-real-stack.ps1"} |
| Required handoff asset scripts/dev/start-real-stack.bat | pass | {"path": "scripts/dev/start-real-stack.bat"} |
| Required handoff asset scripts/ci/verify_self_hosted_package.py | pass | {"path": "scripts/ci/verify_self_hosted_package.py"} |
| Required handoff asset scripts/ci/collect_team_handoff_report.py | pass | {"path": "scripts/ci/collect_team_handoff_report.py"} |
| Required handoff asset scripts/ci/collect_external_self_hosted_install_evidence.py | pass | {"path": "scripts/ci/collect_external_self_hosted_install_evidence.py"} |
| Required handoff asset scripts/ci/rehearse_runnable_self_hosted_package.py | pass | {"path": "scripts/ci/rehearse_runnable_self_hosted_package.py"} |
| Required handoff asset scripts/ci/start-engine-smoke.ps1 | pass | {"path": "scripts/ci/start-engine-smoke.ps1"} |
| Required handoff asset scripts/ci/start-api-smoke.ps1 | pass | {"path": "scripts/ci/start-api-smoke.ps1"} |
| Required handoff asset scripts/ci/start-web-smoke.ps1 | pass | {"path": "scripts/ci/start-web-smoke.ps1"} |
| Required handoff asset package.json | pass | {"path": "package.json"} |
| Required handoff asset pnpm-lock.yaml | pass | {"path": "pnpm-lock.yaml"} |
| Required handoff asset pnpm-workspace.yaml | pass | {"path": "pnpm-workspace.yaml"} |
| Required handoff asset docker-compose.yml | pass | {"path": "docker-compose.yml"} |
| Required handoff asset apps/api/package.json | pass | {"path": "apps/api/package.json"} |
| Required handoff asset apps/api/src/server.ts | pass | {"path": "apps/api/src/server.ts"} |
| Required handoff asset apps/web/package.json | pass | {"path": "apps/web/package.json"} |
| Required handoff asset apps/web/app/page.tsx | pass | {"path": "apps/web/app/page.tsx"} |
| Required handoff asset apps/web/playwright.config.ts | pass | {"path": "apps/web/playwright.config.ts"} |
| Required handoff asset services/engine/pyproject.toml | pass | {"path": "services/engine/pyproject.toml"} |
| Required handoff asset services/engine/uv.lock | pass | {"path": "services/engine/uv.lock"} |
| Required handoff asset services/engine/app/main.py | pass | {"path": "services/engine/app/main.py"} |
| Required handoff asset services/engine/alembic/env.py | pass | {"path": "services/engine/alembic/env.py"} |
| Required handoff asset packages/prompts/decision-screening.md | pass | {"path": "packages/prompts/decision-screening.md"} |
| Required handoff asset packages/prompts/decision-extraction.md | pass | {"path": "packages/prompts/decision-extraction.md"} |
| Required handoff asset infra/docker/postgres/init-extensions.sql | pass | {"path": "infra/docker/postgres/init-extensions.sql"} |
| Required handoff asset infra/docker/redis/redis.conf | pass | {"path": "infra/docker/redis/redis.conf"} |
| README references rehearse_clean_self_hosted_install.py | pass | {"needle": "rehearse_clean_self_hosted_install.py"} |
| README references verify_self_hosted_package.py | pass | {"needle": "verify_self_hosted_package.py"} |
| README references self-hosted.env.example | pass | {"needle": "self-hosted.env.example"} |
| Copied package passes offline verifier | pass | {"blocker_count": 0, "checked_file_count": 276} |

## Source Evidence

| Evidence | Status | Path | Details |
| --- | --- | --- | --- |
| Release evidence | warning | .tmp/runnable-release-evidence.json | {"generated_at": "2026-07-16T08:09:01.509607+00:00", "overall_status": "warning"} |
| Hosted/operator readiness | operator_guided | .tmp/runnable-hosted-operator-readiness.json | {"generated_at": "2026-07-16T08:09:02.096257+00:00", "overall_status": "operator_guided"} |
| Benchmark comparison | pass | .tmp/customer-host-trial-benchmark-comparison.json | {"generated_at": "2026-07-15T05:21:29.801665+00:00", "summary": {"improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 5}} |
| Readiness evidence history | pass | docs/evidence/readiness/index.json | {"generated_at": "2026-07-15T05:51:28.866896+00:00"} |
| Package verification | pass | .tmp/self-hosted-package-verification.json | {"commit": "working-tree", "generated_at": "2026-07-16T08:07:31.551180+00:00", "package_label": "runnable-preview-20260716", "package_path": "<workspace>/.tmp/self-hosted-packages/runnable-preview-20260716", "runnable_status": "pass", "status": "pass", "version_label": "2026-07-16-preview"} |
| Public GitHub import rehearsal | warning | .tmp/githits-live-core-loop.json | {"generated_at": "2026-07-16T07:24:26.081419+00:00", "status": "warning", "summary": {}} |
| License and support boundary | not_provided | - | {"rerun_condition": "Provide --license-support-json."} |
| Team handoff report | not_provided | - | {"rerun_condition": "Provide --team-handoff-json."} |
| External self-hosted install evidence | not_provided | - | {"rerun_condition": "Provide --external-install-evidence-json."} |
| Runnable package rehearsal | pass | .tmp/runnable-self-hosted-package-rehearsal.json | {"commit": "working-tree", "generated_at": "2026-07-16T08:08:25.174227+00:00", "host_profile": {"host_class": "local-isolated-copy", "is_customer_controlled": false, "os_family": "windows"}, "host_proof_level": "independent_host_package_smoke", "label": "runnable-package-20260716", "package_copy": "<temp>/decisionatlas-runnable-package-rehearsal/runnable-package-20260716/package-copy", "status": "pass", "summary": {}, "version_label": "2026-07-16-preview"} |

## Live Stack Probes

| Probe | Status | Details |
| --- | --- | --- |
| Live stack probing | operator_guided | {"reason": "probe_not_requested"} |

## Deferred Product Lanes

- `billing`
- `hosted_multi_tenancy`
- `marketplace_or_self_service_oauth`
- `hosted_secret_vault`
- `enterprise_sso`
- `online_license_server`
- `runtime_license_enforcement`

## Limitations

- This rehearsal validates a clean runnable package copy and evidence bundle, not a customer-server install unless separate customer-controlled evidence is attached.
- External/customer-host install proof must be supplied separately through external install evidence.
- A passing GitHub-hosted runner rehearsal proves package independence but remains is_customer_controlled=false.
- Live URL probing is optional and must remain non-pass when URLs are not provided or unreachable.
- Secrets, repository tokens, .env files, private repository dumps, and database backups are not included.

## Recommended Next Actions

- Review non-pass evidence lanes and either rerun with the missing input or disclose the operator-guided limitation.
- Archive clean install rehearsal evidence into readiness history before customer handoff.
