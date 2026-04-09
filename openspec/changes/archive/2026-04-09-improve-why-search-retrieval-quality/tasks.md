## 1. Query Rewrite And Ranking

- [x] 1.1 Expand `rewrite_query()` with stronger technical alias normalization while preserving question intent.
- [x] 1.2 Benchmark and rebalance hybrid retrieval weights so vector scores materially affect accepted-decision recall.
- [x] 1.3 Add regression coverage for equivalent why phrasings that should map to the same accepted decision.

## 2. Supporting Evidence Retrieval

- [x] 2.1 Add artifact-chunk retrieval as a supporting evidence layer behind selected accepted decisions.
- [x] 2.2 Update why answer assembly so retrieval-backed evidence can strengthen explanation quality without broadening the main answer into unrelated decisions.
- [x] 2.3 Keep existing evidence-state semantics intact while allowing stronger support when retrieval finds better grounded evidence.

## 3. Validation

- [x] 3.1 Add engine and API regression coverage for chunk-backed why evidence and support-state upgrades.
- [x] 3.2 Add web regression coverage if imported why rendering changes for richer support context or stronger support states.
- [x] 3.3 Run benchmark-style validation against real imported why questions before closing the change.
