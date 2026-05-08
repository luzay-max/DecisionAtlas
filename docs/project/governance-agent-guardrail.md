# Governance Agent Guardrail

DecisionAtlas governance agent guardrail is a local advisory layer for AI agents. It aggregates:

- governance diff checker: current workspace diff vs accepted rules, OpenSpec context, roadmap direction, and validation expectations;
- governance drift detector: long-term consistency across roadmap, main specs, archived changes, update logs, postmortems, accepted rules, and current diff context.

The guardrail is designed to help an AI agent decide whether it can continue, should proceed with caution, or must pause for human review. It does not replace tests, review, or OpenSpec discipline.

## Run It

From the repository root:

```powershell
python scripts/governance/agent_guardrail.py --pretty
```

For a concise local summary:

```powershell
python scripts/governance/agent_guardrail.py --summary
```

For offline governance rules exported from the API:

```powershell
python scripts/governance/agent_guardrail.py --rules-json rules.json --pretty
```

The command exits with `0` by default, including `caution` and `pause` advisory results. A future explicit CI gate can change that behavior, but this first version is not a blocker.

For an opt-in local enforcement preview:

```powershell
python scripts/governance/agent_guardrail.py --enforcement-preview local-strict --pretty
```

This does not change default guardrail behavior. It adds an `enforcement_preview` object that answers whether stricter governance would block based on the current advisory result.

To make local strict preview fail only on would-block results:

```powershell
python scripts/governance/agent_guardrail.py --enforcement-preview local-strict --strict-exit
```

Use `--strict-exit` only in explicitly opted-in local workflows. Do not wire it into the default release baseline unless a future OpenSpec change makes that decision.

For local report text suitable for a PR comment or release checklist note:

```powershell
python scripts/governance/agent_guardrail.py --enforcement-preview pr-annotation --summary
python scripts/governance/agent_guardrail.py --enforcement-preview release-checklist --summary
```

These modes generate local text only. They do not call GitHub, post comments, mutate release gates, or require network access.

## Workflow Checkpoints

AI agents and developers should run the guardrail at four local workflow checkpoints:

- Before implementation, when a task is likely to modify code, specs, roadmap, governance docs, or project direction.
- After implementation, before claiming a change is complete and after targeted validation has been selected or run.
- Before archiving an OpenSpec change.
- Before committing completed work.

This is especially important when the work touches accepted rules, roadmap stage transitions, private repository access, import/review behavior, governance documents, or validation expectations.

When the summary is `caution` or `pause`, include the evidence in the handoff instead of hiding it behind a green test result.

## Governed Hosted Preview

For a governed hosted preview, run the guardrail before claiming the governance lane is ready:

```powershell
python scripts/governance/agent_guardrail.py --summary
```

Use the result as readiness evidence, not as enforcement:

- `continue`: the governed preview can proceed after targeted validation.
- `caution`: the preview can proceed only if the caution evidence is addressed or disclosed in the readiness handoff.
- `pause`: stop and ask for human review before presenting the guardrail as positive governed-preview evidence.

During an external walkthrough, explain that the guardrail is advisory project governance memory. It does not automatically accept Markdown rule drafts, rewrite code, update OpenSpec artifacts, or block CI by default.

Optional enforcement preview output may be recorded as additional readiness evidence:

```powershell
python scripts/governance/agent_guardrail.py --enforcement-preview release-checklist --summary
```

Record the preview status, source evidence, and any human override note. Treat it as operator-guided evidence, not as default CI enforcement.

## Agent Workflow Protocol

The guardrail JSON includes a tool-agnostic workflow protocol for Codex, OpenCode, Claude, or another agent consuming the result:

- `workflow_protocol`: protocol name, version, and `advisory_only` marker.
- `agent_instruction`: short imperative guidance for the current status.
- `allowed_next_actions`: what the agent may do next.
- `disallowed_next_actions`: what the agent must not do without human review.
- `human_questions`: concrete questions to ask when human review is required.
- `handoff_summary`: reusable machine-readable governance summary for final responses, PR descriptions, or commit handoffs.

The protocol is deterministic and derived from the same diff, drift, rules, required tests, and human-decision evidence already present in the guardrail result. It does not call an external LLM.

## Status Semantics

### `continue`

The current diff checker passes and the drift detector is clean or informational.

The agent may continue normal work, but this is not a correctness proof. It still needs targeted tests, normal review, and OpenSpec validation when applicable.

Typical protocol action:

```text
allowed_next_actions:
- continue_implementation
- run_required_tests
- record_governance_handoff
```

### `caution`

The guardrail found non-blocking concerns, such as:

- warning-level diff findings;
- weak roadmap alignment;
- `watch` or `drift_detected` drift signals that do not require a human decision;
- recommended validation or documentation follow-up.

The agent may continue only after addressing or explicitly reporting the recommended next actions.

Typical protocol action:

```text
allowed_next_actions:
- address_recommended_next_actions
- run_required_tests
- continue_with_explicit_caution_handoff
```

The agent must not claim completion while hiding caution evidence.

### `pause`

The agent must stop and ask for human review when the guardrail detects:

- blocked diff check;
- accepted-rule conflict;
- missing OpenSpec context for non-trivial behavior changes;
- missing validation evidence for implementation changes;
- drift report `review_required`;
- unsynced human decision;
- human decision needed before governance context can be trusted.

The agent must not silently resolve a `pause` by rewriting code, specs, roadmap, governance documents, or accepted rules. The correct next step is to show the evidence and ask the human what decision should be made.

`pause` remains advisory by default. It is a stop-and-ask signal for agents, not an automatic CI failure or an instruction to mutate project files.

Typical protocol action:

```text
allowed_next_actions:
- summarize_guardrail_evidence
- ask_human_for_decision
- record_governance_handoff

disallowed_next_actions:
- continue_implementation_without_human_review
- commit_without_human_review
- silently_rewrite_code_to_clear_guardrail
- silently_rewrite_openspec_to_clear_guardrail
- silently_rewrite_roadmap_or_governance_rules_to_clear_guardrail
```

If `human_questions` is present, the agent should ask those questions directly and cite the associated findings, signals, or source results.

## Output Contract

The JSON output includes stable fields for agent consumption:

- `agent_status`: `continue`, `caution`, or `pause`;
- `summary`: compact interpretation for humans and agents;
- `findings`: normalized current-diff governance findings;
- `signals`: normalized long-term drift signals;
- `matched_rules`: accepted governance rules matched by the diff checker;
- `required_tests`: validation expectations from OpenSpec tasks, diff analysis, and rules;
- `human_decisions_needed`: decisions that need human review;
- `recommended_next_actions`: concrete next steps;
- `workflow_protocol`: protocol metadata for agent consumption;
- `agent_instruction`: status-specific instruction;
- `allowed_next_actions`: permitted next actions;
- `disallowed_next_actions`: forbidden next actions without human review;
- `human_questions`: concrete questions with evidence references;
- `handoff_summary`: reusable governance summary;
- `source_results`: raw diff checker and drift detector outputs for traceability.

Agents should cite `source_results` evidence when explaining why they paused or proceeded with caution.

When `--enforcement-preview <mode>` is supplied, JSON output also includes:

- `enforcement_preview.mode`: `local-strict`, `pr-annotation`, or `release-checklist`;
- `enforcement_preview.would_block`: whether stricter governance would block;
- `enforcement_preview.severity`: `pass`, `warning`, or `blocker`;
- `enforcement_preview.block_reasons`: source-derived reasons for a would-block result;
- `enforcement_preview.warning_reasons`: source-derived non-blocking warning evidence;
- `enforcement_preview.override_required`: whether a human override handoff is needed;
- `enforcement_preview.override_prompt`: how to record a false-positive override;
- `enforcement_preview.source_evidence`: guardrail findings, signals, questions, actions, and source results;
- `enforcement_preview.report_text`: local Markdown-style text for summaries, PR annotations, or release checklist notes.

The preview is derived from the advisory result. It does not replace `agent_status`.

## Handoff Summary Format

Use `handoff_summary` in final responses, PR descriptions, and commit handoffs:

```text
Governance:
- Agent status: <continue|caution|pause>
- Diff status: <pass|warning|blocked>
- Drift status: <clean|watch|drift_detected|review_required>
- Required tests: <list or none>
- Recommended actions: <list or none>
- Human questions: <list or none>
- Advisory only: true
```

If the status is `caution` or `pause`, include the evidence or human question even when all tests pass.

## Enforcement Preview Semantics

Enforcement preview is opt-in and derived from the same guardrail result:

- `continue`: preview passes; targeted validation is still required.
- `caution`: preview warns; disclose or address evidence before claiming completion.
- `pause`: preview would block in local strict mode until a human decision is recorded.
- diff check `blocked`: preview would block.
- drift report `review_required`: preview would block.

The preview keeps `advisory_default: true` so consumers do not confuse local strict preview with default CI enforcement.

## False-Positive Override Handoff

If strict preview reports `would_block: true` and the human decides it is a false positive, record a human-authored override in the handoff:

```text
Governance override:
- Preview mode: <local-strict|pr-annotation|release-checklist>
- Would block: true
- Human decision: <why the agent may continue>
- Evidence cited: <finding/signal/source_result ids or summary>
- Follow-up: <none|update specs|update accepted rule|add validation>
```

The guardrail does not write this override automatically. The human decision may later become OpenSpec or accepted-rule work, but that remains a separate explicit change.

## Agent Examples

Codex-style local implementation:

```text
1. Run `python scripts/governance/agent_guardrail.py --summary` before implementation.
2. Implement only if status is `continue` or the `caution` actions are addressed or disclosed.
3. Run targeted tests and `openspec validate --all --strict`.
4. Run the guardrail again before archive and commit.
5. Include `handoff_summary` in the final response.
```

OpenCode or Claude-style handoff:

```text
If status is `pause`, stop editing. Summarize `findings`, `signals`, and `human_questions`, then ask the human for the decision needed before continuing.
```

## Non-Goals

The guardrail does not:

- modify application code;
- rewrite OpenSpec artifacts;
- update roadmap documents;
- create or accept governance rules;
- block CI by default;
- post PR annotations to GitHub;
- persist override decisions to the database;
- require an external LLM provider.
