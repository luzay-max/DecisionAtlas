## 1. Checker Contract And Entry Point

- [x] 1.1 Define the governance check result schema with `status`, `findings`, `matched_rules`, `conflicts`, `required_tests`, and `recommended_next_action`.
- [x] 1.2 Add the first local governance check entrypoint for the current workspace diff.
- [x] 1.3 Ensure the entrypoint can return machine-readable JSON for future AI/tool calls.

## 2. Context Collection

- [x] 2.1 Collect the current git diff, including staged and unstaged changes.
- [x] 2.2 Collect active OpenSpec proposal, design, specs, and tasks when an active change exists.
- [x] 2.3 Collect bounded main spec and roadmap context for project-direction checks.
- [x] 2.4 Collect accepted governance rules and source metadata without treating pending or rejected drafts as enforceable.

## 3. Governance Evaluation

- [x] 3.1 Detect non-trivial behavior changes that lack active OpenSpec context.
- [x] 3.2 Match current diff signals against accepted governance rules and return source-linked findings.
- [x] 3.3 Detect ambiguous roadmap/spec alignment and downgrade uncertain cases to warnings instead of blockers.
- [x] 3.4 Detect missing validation or test evidence from code changes and OpenSpec tasks.
- [x] 3.5 Compute the overall `pass`, `warning`, or `blocked` status from finding severities.

## 4. Documentation And Tests

- [x] 4.1 Add fixtures for pass, warning, and blocked governance check scenarios.
- [x] 4.2 Add tests for missing OpenSpec context, accepted-rule conflict, ignored pending/rejected rules, and missing validation evidence.
- [x] 4.3 Document how to run the checker and how to interpret advisory results.
- [x] 4.4 Run targeted checker tests and OpenSpec strict validation.
- [x] 4.5 Run the practical project validation gate or document any environment-limited skip.
