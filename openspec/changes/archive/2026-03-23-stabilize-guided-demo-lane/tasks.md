## 1. Guided Demo Entry And Navigation

- [x] 1.1 Rework the homepage so the guided demo is the primary CTA and provider/live-analysis controls move into an explicitly labeled advanced or experimental section
- [x] 1.2 Add reusable guided-demo framing UI for step number, purpose text, and next recommended action
- [x] 1.3 Update workspace navigation so guided-demo pages emphasize the walkthrough path while keeping advanced controls secondary

## 2. Dashboard And Demo Import Guidance

- [x] 2.1 Add guided-demo progress and next-step cues to the demo workspace dashboard using existing workspace read-model signals
- [x] 2.2 Upgrade the demo import interaction to show stage-aware progress, terminal outcomes, and completion-oriented next actions
- [x] 2.3 Ensure dashboard and import empty/error states preserve walkthrough orientation instead of leaving the user to infer the next step

## 3. Step-by-Step Walkthrough Pages

- [x] 3.1 Update the review experience to show guided-demo step context, explain the review goal, and present an explicit handoff to why-search after completion
- [x] 3.2 Update why-search to start from a guided action, reinforce demo context, and hand off explicitly to the timeline step
- [x] 3.3 Update timeline and drift pages to show walkthrough step context, page purpose, and clear continuation or completion actions

## 4. Provenance Boundaries, Copy, And Validation

- [x] 4.1 Extend provenance and expectation-setting copy so review surfaces and advanced-entry surfaces clearly distinguish seeded walkthrough behavior from imported or experimental behavior
- [x] 4.2 Update demo script and related walkthrough copy to match the new guided-demo-first product narrative
- [x] 4.3 Add or update automated tests that cover guided-demo entry priority, advanced-section demotion, step guidance, and provenance boundary messaging
