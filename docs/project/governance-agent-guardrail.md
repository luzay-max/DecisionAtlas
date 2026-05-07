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

## Workflow Checkpoints

AI agents and developers should run the guardrail at four local workflow checkpoints:

- Before implementation, when a task is likely to modify code, specs, roadmap, governance docs, or project direction.
- After implementation, before claiming a change is complete and after targeted validation has been selected or run.
- Before archiving an OpenSpec change.
- Before committing completed work.

This is especially important when the work touches accepted rules, roadmap stage transitions, private repository access, import/review behavior, governance documents, or validation expectations.

When the summary is `caution` or `pause`, include the evidence in the handoff instead of hiding it behind a green test result.

## Status Semantics

### `continue`

The current diff checker passes and the drift detector is clean or informational.

The agent may continue normal work, but this is not a correctness proof. It still needs targeted tests, normal review, and OpenSpec validation when applicable.

### `caution`

The guardrail found non-blocking concerns, such as:

- warning-level diff findings;
- weak roadmap alignment;
- `watch` or `drift_detected` drift signals that do not require a human decision;
- recommended validation or documentation follow-up.

The agent may continue only after addressing or explicitly reporting the recommended next actions.

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
- `source_results`: raw diff checker and drift detector outputs for traceability.

Agents should cite `source_results` evidence when explaining why they paused or proceeded with caution.

## Non-Goals

The guardrail does not:

- modify application code;
- rewrite OpenSpec artifacts;
- update roadmap documents;
- create or accept governance rules;
- block CI by default;
- require an external LLM provider.
