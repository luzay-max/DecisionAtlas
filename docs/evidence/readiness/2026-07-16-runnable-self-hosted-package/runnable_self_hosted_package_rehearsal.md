# Runnable Self-Hosted Package Rehearsal

- Generated at: `2026-07-16T08:08:25.174227+00:00`
- Status: `pass`
- Host proof: `independent_host_package_smoke`
- Host class: `local-isolated-copy`
- Customer controlled: `False`
- Repository: `githits-com/githits-cli`
- Package copy: `<temp>/decisionatlas-runnable-package-rehearsal/runnable-package-20260716/package-copy`

## Stages

| Stage | Status | Details |
| --- | --- | --- |
| Copy package into isolated runtime root | pass | {"package_copy": "<temp>/decisionatlas-runnable-package-rehearsal/runnable-package-20260716/package-copy", "source_package": "<workspace>/.tmp/self-hosted-packages/runnable-preview-20260716"} |
| Verify runnable package inputs | pass | {"blocker_ids": [], "runnable_status": "pass"} |
| Install exact Node and Python dependencies | pass | {"requested": true} |
| Install Playwright Chromium | pass | {"requested": true} |
| Start engine, API, and web with health gates | pass | {"duration_seconds": 32.967, "proof_mechanism": "playwright_web_server_health_gates", "requested": true, "urls": {"api": "http://127.0.0.1:3001/health", "engine": "http://127.0.0.1:8000/health", "web": "http://127.0.0.1:3000"}} |
| Run imported-workspace browser smoke | pass | {"repository": "githits-com/githits-cli", "requested": true} |

## Limitations

- Dependency installation downloads packages unless an operator supplies an approved cache or mirror.
- GitHub-hosted and local isolated rehearsals prove package independence but are not customer-controlled-host proof.
- Evidence stores only bounded command tails and does not store tokens, raw private source, databases, or raw model output.

## Next Actions

- Repeat the same runnable package rehearsal on a sanitized customer-controlled host before clean customer claims.
