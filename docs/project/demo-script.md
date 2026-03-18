# Demo Script

This walkthrough is designed for a 60-90 second open-source demo.

## 1. Open the workspace dashboard

Route:

- `http://localhost:3000/workspaces/demo-workspace`

Narration:

- "DecisionAtlas starts with one workspace and shows the current artifact count, accepted decisions, candidate decisions, and recent alerts."

## 2. Show the review queue

Route:

- `http://localhost:3000/review`

Narration:

- "Candidate decisions are not auto-promoted. They wait in a review queue so the system stays evidence-first and human-approved."

## 3. Show why-search

Route:

- `http://localhost:3000/search`

Suggested question:

- `why use redis cache`

Narration:

- "Why-answers fail closed when evidence is weak. When evidence exists, every answer carries direct citations."

## 4. Show the timeline

Route:

- `http://localhost:3000/timeline`

Narration:

- "Accepted decisions become a time-ordered memory instead of disappearing into issues and pull requests."

## 5. Show drift alerts

Route:

- `http://localhost:3000/drift`

Narration:

- "Rule-first drift detection catches high-signal contradictions, and semantic drift adds conservative review flags when a new artifact may supersede an older decision."

## Closing line

- "The product is not training a new model. It is turning engineering decisions into durable, reviewable, searchable operating memory."
