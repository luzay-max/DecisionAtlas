## 1. Customer Host Trial Contract

- [x] 1.1 Extend the real external host trial input schema with bounded package, startup, health, administrator login, team/workspace, repository import, review, Why, Drift, continuity, browser, and redaction lane records while accepting legacy inputs.
- [x] 1.2 Add a sanitized `templates/customer-host-trial.example.json` and document which fields must be filled on the target host versus which must never be copied into evidence.
- [x] 1.3 Add a reusable operator checklist and command sequence to the self-hosted delivery runbook, including package identity, startup, health, first login, account/workspace setup, public/private repository boundary, core review flow, backup/recovery, and archive steps.

## 2. Evidence Collector And Safety

- [x] 2.1 Update `collect_real_external_host_trial_evidence.py` to aggregate the new lanes, derive honest proof levels, preserve non-clean states, and emit bounded next actions.
- [x] 2.2 Redact absolute paths from host/source inputs, Markdown, warnings, and readiness-history references; preserve token/private-source/raw-backup blocking behavior without rendering sensitive values.
- [x] 2.3 Keep source evidence summaries bounded and compatible with existing customer-host v2 and full-chain evidence, without changing required-gate semantics.

## 3. Regression And Real Trial Verification

- [x] 3.1 Add focused tests for complete sanitized input, legacy input, missing core lanes, template markers, secret markers, external path redaction, proof-level classification, and archive output.
- [x] 3.2 Run package verification, clean-install rehearsal, continuity rehearsal, OpenSpec strict validation, focused tests, full engine tests, Node tests, typecheck, and benchmark fixture validation.
- [x] 3.3 Execute the operator checklist against an isolated self-hosted host or an independently controlled external host using a fresh public GitHub repository; preserve the real result as `pass`, `warning`, `operator_guided`, or `blocking` without fabricating customer proof.

## 4. Delivery Evidence And Closeout

- [x] 4.1 Generate JSON/Markdown trial, release, hosted readiness, continuity, handoff, and readiness-history evidence with no secrets, raw source, raw model output, or absolute local paths.
- [x] 4.2 Update the completion taskbook, dated update log, and next-development plan with actual host boundary, verification results, unresolved external-host requirements, and the next pilot priority.
- [ ] 4.3 Archive the OpenSpec change, commit scoped files on the dedicated branch, push it, run and inspect GitHub Actions, and report the exact CI result.
