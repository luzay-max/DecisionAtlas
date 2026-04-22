# Demo Script

This walkthrough is designed for a 60-90 second product demo. The primary story is still the stable guided lane, but the imported-workspace lane is now strong enough for a short credibility check at the end.

## Opening posture

Route:

- `http://localhost:3000/`

Narration:

- "Tonight's main path is the guided demo. It uses seeded walkthrough data so the product story stays stable."
- "Live analysis and provider controls still exist, but they are intentionally moved into an advanced section because they are not required for the core demo."

## 1. Open the guided demo workspace

Route:

- `http://localhost:3000/workspaces/demo-workspace`

Narration:

- "The dashboard is now the walkthrough control panel. It tells us which step we are on and what to do next."
- "The provenance banner makes it explicit that this workspace is seeded demo data, not imported repository output."

## 2. Run or confirm the demo import

Route:

- `http://localhost:3000/workspaces/demo-workspace`

Narration:

- "If the demo needs to be reset, the import action now shows stage-aware progress instead of leaving the audience guessing."
- "Once the workspace is ready, the UI points directly to the review step."

## 3. Show the review queue

Route:

- `http://localhost:3000/review?workspace=demo-workspace`

Narration:

- "Candidate decisions are not auto-promoted. The review step makes the human checkpoint explicit."
- "The page explains the goal of this step and hands us off directly to why-search when we're done."

## 4. Show why-search

Route:

- `http://localhost:3000/search?workspace=demo-workspace`

Suggested question:

- `why use redis cache`

Narration:

- "Why-search starts from a recommended demo question, so we do not need to improvise during the walkthrough."
- "When evidence exists, the answer includes citations. When it doesn't, the system fails closed instead of bluffing."

## 5. Show the timeline

Route:

- `http://localhost:3000/timeline?workspace=demo-workspace`

Narration:

- "Accepted decisions become a time-ordered memory instead of disappearing into issues and pull requests."
- "The guided demo framing keeps the story moving and points clearly to the drift step."

## 6. Show drift alerts and close

Route:

- `http://localhost:3000/drift?workspace=demo-workspace`

Narration:

- "Drift makes the memory operational by checking newer artifacts against accepted decisions."
- "The last step closes the loop and makes it obvious that we completed the demo lane, not an experimental analysis flow."

## Closing line

- "DecisionAtlas is not training a new model. It is turning engineering decisions into durable, reviewable, searchable operating memory."

## Optional 30-second real-repo proof

This is an operator-guided credibility check, not part of the core guided walkthrough and not part of the default offline release gate.

Route:

- `http://localhost:3000/`

Narration:

- "The seeded lane is our stable walkthrough, but the same product can also analyze a real public GitHub repository into a separate imported workspace."
- "That imported workspace now exposes whether review, why-search, and drift are ready, instead of leaving the operator to guess the next move."
- "The imported why answers stay anchored to accepted decisions, with artifact chunks acting as supporting evidence rather than replacing the trust anchor."
- "We use this as a bounded proof of real capability, not as the primary demo story."
