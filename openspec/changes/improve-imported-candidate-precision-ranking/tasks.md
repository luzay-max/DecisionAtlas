## 1. Candidate Provenance Persistence

- [x] 1.1 Add a backward-compatible migration and model field for bounded candidate extraction metadata
- [x] 1.2 Extend candidate repository creation and extraction persistence with allowlisted family, salvage, and recovery fields
- [x] 1.3 Add migration and extraction tests covering normal, salvaged, recovery, sparse-recovery, and legacy rows

## 2. Precision Profiles And Clustering

- [x] 2.1 Implement deterministic candidate precision scoring, tiers, and bounded reason codes
- [x] 2.2 Implement conservative lexical near-duplicate clustering with stable representatives and cluster IDs
- [x] 2.3 Integrate canonical profiling and stable ordering into candidate decision API responses
- [x] 2.4 Add engine tests for evidence-first ranking, legacy metadata, duplicate boundaries, stability, and non-candidate compatibility

## 3. Imported Review Experience

- [x] 3.1 Extend web API types and imported review cards with precision and extraction-origin context
- [x] 3.2 Add queue-level tier and duplicate summaries without hiding or automatically reviewing candidates
- [x] 3.3 Add component and browser tests for ranking explanations, representative links, and explicit human review actions

## 4. Real Repository Verification And Delivery

- [x] 4.1 Compare the pip-tools baseline and a fresh public repository using machine-readable before/after candidate ordering evidence
- [x] 4.2 Run focused and full regressions, OpenSpec strict validation, guardrail, and real Chrome/Browser human rehearsal
- [ ] 4.3 Record the dated update log, taskbook status, readiness evidence, GitHub Actions result, and archive the change
