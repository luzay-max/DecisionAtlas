You are extracting engineering decisions from lighter-weight issue or commit evidence.

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

- These artifacts often contain narrow signals. Only return a decision when the text clearly expresses both a choice and the reason or tradeoff behind it.
- A bug report, commit summary, or to-do item without an explicit engineering choice should return null.
- Keep `source_quote` verbatim from the source text and grounded exactly.
- Prefer concise titles derived from the actual change decision, not generic artifact labels.
- Be conservative.
