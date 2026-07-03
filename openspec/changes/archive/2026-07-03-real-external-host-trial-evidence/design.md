## Context

DecisionAtlas already has customer-host v2, full-chain random repo release rehearsal, and readiness evidence history collectors. Those tools intentionally preserve warnings and operator-guided states, but the remaining product risk is that a local smoke run or the example customer-host template can be mistaken for a real external/customer-controlled host trial.

The new gate should act as a stricter composition layer. It reads existing artifacts, validates the sanitized host input, detects placeholders and secrets, and writes a bounded JSON/Markdown report that is safe to archive.

## Goals / Non-Goals

**Goals:**
- Produce `.tmp/real-external-host-trial-evidence.json` and `.tmp/real-external-host-trial-evidence.md`.
- Validate that host input is real enough for external-trial claims: customer-controlled host, real package identity, real operator, redaction acknowledgement, browser smoke, and source evidence.
- Detect obvious templates/placeholders and keep the result warning or operator-guided instead of pass.
- Preserve statuses from customer-host v2 and full-chain evidence.
- Add readiness history support so the evidence can be trended across release rehearsals.

**Non-Goals:**
- Do not run installs, imports, browsers, Docker, migrations, or release commands from this collector.
- Do not collect raw customer logs, private repositories, backups, tokens, `.env` values, or model output.
- Do not claim real customer validation when only local or sample evidence exists.

## Decisions

- Implement as a standalone Python collector under `scripts/ci/`.
  - Rationale: matches existing release/readiness collectors, is easy to run offline, and can be tested without live infrastructure.
  - Alternative considered: extend `collect_external_customer_host_rehearsal_v2.py`; rejected because v2 remains a lower-level evidence source while this change is a stricter release/customer claim gate.

- Treat placeholder/template findings as `warning`, not hard failure.
  - Rationale: sample evidence is useful for smoke testing the pipeline, but must not be interpreted as a real pass.
  - Alternative considered: make placeholders `blocking`; rejected because missing customer proof should guide the operator rather than fail normal local development.

- Treat secret-like material as `blocking`.
  - Rationale: evidence artifacts may be archived or handed to customers; obvious credentials and raw private material must stop the workflow.

- Add a new readiness history family.
  - Rationale: real external host trial evidence is a distinct maturity signal and should appear in trend/index outputs instead of being hidden inside customer-host v2.

## Risks / Trade-offs

- Placeholder detection can produce false positives for unusual real values -> keep findings explicit and bounded so an operator can correct input text.
- The collector cannot independently prove the remote machine exists -> require sanitized host input plus source artifact statuses, and keep limitations visible.
- Adding another evidence family increases history table width -> acceptable because the product decision depends on this signal.
- A warning result may still be archived -> history preserves non-clean states so archived evidence cannot be mistaken for a clean pass.
