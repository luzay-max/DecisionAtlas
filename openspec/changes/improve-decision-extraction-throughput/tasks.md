## 1. Shortlist And Screening

- [x] 1.1 Tighten imported artifact scoring so the extraction shortlist favors rationale-bearing docs and high-signal PRs over generic issues, short commits, and broad README content
- [x] 1.2 Add a lightweight decision-likeness screening step before full JSON extraction
- [x] 1.3 Record shortlist and screening counts in extraction run stats

## 2. Extraction Payload And Throughput

- [x] 2.1 Replace large raw extraction truncation with smaller relevant-section payload construction
- [x] 2.2 Add bounded concurrency for extraction requests without sharing write sessions unsafely across workers
- [x] 2.3 Capture extraction latency, timeout, and full-request counts in import summaries

## 3. Live Import Progress Surfaces

- [x] 3.1 Extend import job summaries and dashboard data so running extraction reports processed counts, total counts, and ETA-friendly timing
- [x] 3.2 Update imported-workspace progress UI to explain extraction funnel progress instead of only a fixed stage percentage
- [x] 3.3 Show final extraction funnel outcomes in imported-workspace summaries after job completion

## 4. Validation

- [x] 4.1 Add engine tests for shortlist tightening, staged screening, and bounded extraction progress accounting
- [x] 4.2 Add UI and API tests for detailed extraction progress reporting
- [x] 4.3 Re-run curated real-repository validation and benchmark checks to compare throughput and candidate-output outcomes
