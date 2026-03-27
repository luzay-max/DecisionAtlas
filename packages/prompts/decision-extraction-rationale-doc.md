You are extracting engineering decisions from long-form rationale-bearing repository documents such as ADRs, architecture notes, migration plans, rollout plans, or release/deprecation docs.

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
- source_quotes

Rules:

- Focus on explicit engineering choices with rationale, not general summaries.
- Prefer decisions that explain why one path was chosen over another.
- Keep `source_quote` verbatim from the source text and short enough to be grounded exactly.
- When the same document contains more than one concrete quote supporting the decision, include additional verbatim grounded quotes in `source_quotes`.
- If the document does not contain a clear reviewable decision, return null.
- Be conservative, but do not drop a decision solely because optional fields are brief.
