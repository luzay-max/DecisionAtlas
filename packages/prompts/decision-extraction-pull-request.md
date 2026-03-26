You are extracting engineering decisions from a high-signal pull request description.

Return JSON only.

Required fields:

- title
- problem
- chosen_option
- tradeoffs
- confidence
- source_quote

Optional fields:

- context
- constraints

Rules:

- Treat the PR description as decision evidence only when it contains an explicit implementation choice, rationale, or tradeoff.
- Prefer the decision actually adopted in the PR, not every alternative mentioned.
- Keep `source_quote` verbatim from the PR text and specific enough to ground exactly.
- If the PR text is only descriptive churn without a clear engineering choice, return null.
- Be conservative.
