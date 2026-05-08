# Governance Drift Detection

Governance drift detection is the Stage 6 advisory report for long-term project direction drift. It is different from the governance diff checker:

- `scripts/governance/check.py` checks the current diff before merge.
- `scripts/governance/drift_report.py` checks whether governance knowledge is becoming inconsistent over time.

The first version is local, deterministic, and report-only. It does not modify code, update OpenSpec files, rewrite governance rules, create new rules, or block CI.

## Run

From the repository root:

```powershell
python scripts\governance\drift_report.py --root . --pretty
```

Optional inputs:

```powershell
python scripts\governance\drift_report.py --root . --owner-scope local-default --pretty
python scripts\governance\drift_report.py --root . --rules-json .\tmp\governance-rules.json --pretty
```

The script can read governance rules from the configured local SQLite database when available. For offline or test usage, pass `--rules-json`.

## Output

The report returns machine-readable JSON:

```json
{
  "status": "clean",
  "signals": [],
  "human_decisions_needed": [],
  "recommended_next_actions": ["No governance drift signals detected. Continue normal review."],
  "context": {
    "roadmap_refs": 1,
    "spec_refs": 35,
    "archived_changes": 12,
    "log_refs": 10,
    "governance_rules": 3,
    "accepted_rule_count": 2,
    "diff_paths": [],
    "advisory_only": true
  }
}
```

## Status

- `clean`: no meaningful governance drift signals were detected.
- `watch`: weak or ambiguous signals exist, but the report is not claiming concrete drift.
- `drift_detected`: concrete evidence suggests inconsistency between governance sources or repeated known issues.
- `review_required`: a human decision is needed before governance context can be trusted.

## Signal Types

- `roadmap_mismatch`: recent change history or diff topics do not clearly align with roadmap or spec terminology.
- `spec_gap`: archived or recent behavior appears to lack a corresponding main OpenSpec spec.
- `stale_rule`: stale, superseded, rejected, or draft governance guidance appears to be reused as active guidance.
- `repeated_postmortem_issue`: a historical issue or error summary appears similar to recent context.
- `unsynced_decision`: proposal, design, task, roadmap, or update-log text appears to contain a human decision that is not clearly reflected in main specs or accepted rules.

## Interpretation

Treat the report as a review aid. A signal means:

1. The report found evidence worth checking.
2. The evidence points to source documents or current diff context.
3. A human should decide whether to update specs, accept a rule, supersede a rule, revise roadmap, or ignore the signal.

It does not mean the code is automatically wrong.

## Rule Lifecycle Interpretation

Drift detection distinguishes accepted/current rules from inactive lifecycle evidence:

- `accepted + active + current` rules count as accepted governance context.
- `accepted + active + stale` and `accepted + active + superseded` rules do not count as current authoritative context.
- If stale or superseded rule text appears in recent diff or archived-change context, the detector emits a `stale_rule` human-review signal with lifecycle evidence.
- A superseded rule should include `superseded_by_rule_id` when a replacement exists; drift output preserves that reference so the reviewer can decide whether recent work should follow the replacement or create a new accepted current rule.

The detector never changes lifecycle status by itself.
