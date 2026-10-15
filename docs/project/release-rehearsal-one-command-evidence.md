# Release Rehearsal One-Command Evidence

This rehearsal gives operators one command to assemble the current release evidence bundle from existing DecisionAtlas evidence lanes.

## Default Command

```powershell
python scripts\ci\collect_release_rehearsal_evidence.py `
  --output-json .tmp\release-rehearsal-evidence.json `
  --output-markdown .tmp\release-rehearsal-evidence.md
```

By default the script discovers existing local evidence from known paths such as:

- `.tmp/release-evidence.json`
- `.tmp/hosted-operator-readiness.json`
- `.tmp/real-repo-benchmark-trend.json`
- `.tmp/real-repo-benchmark-comparison.json`
- `.tmp/multi-repo-live-diagnosis.json`
- `.tmp/agent-guardrail.json`
- `docs/evidence/readiness/index.json`

Missing lanes are preserved as `not_provided`; they are not treated as pass.

## Run Live Multi-Repo Diagnosis

```powershell
python scripts\ci\collect_release_rehearsal_evidence.py `
  --run-multi-repo-diagnosis `
  --repo-id httpx `
  --repo-id fastapi `
  --output-json .tmp\release-rehearsal-evidence.json `
  --output-markdown .tmp\release-rehearsal-evidence.md
```

This runs the multi-repo diagnosis lane first, then includes the generated JSON/Markdown in the release rehearsal bundle.

## Archive To Readiness History

```powershell
python scripts\ci\collect_release_rehearsal_evidence.py `
  --archive-history `
  --output-json .tmp\release-rehearsal-evidence.json `
  --output-markdown .tmp\release-rehearsal-evidence.md
```

The archive copies the bundle to:

```text
docs/evidence/readiness/YYYY-MM-DD-release-rehearsal-one-command/
```

and updates:

```text
docs/evidence/readiness/release-rehearsal-index.json
```

## Evidence Boundary

- The bundle stores compact statuses, counts, source paths, and next actions.
- The bundle must not include tokens, raw private source, raw model output, or unbounded local logs.
- `warning`, `operator_guided`, `not_provided`, `provider_failure`, and `local_stack_failure` are valid evidence states.
- This command does not replace individual lane collectors; it makes the release handoff repeatable.
