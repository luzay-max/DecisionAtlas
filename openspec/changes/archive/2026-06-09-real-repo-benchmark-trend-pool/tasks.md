## 1. Implementation

- [ ] Add a fixed real repository benchmark trend pool configuration.
- [ ] Add a benchmark trend evidence collector that writes JSON and Markdown.
- [ ] Add optional benchmark trend summarization to the team handoff report collector.
- [ ] Document how release rehearsals should use the fixed pool trend evidence.

## 2. Verification

- [x] Add pytest coverage for pool validation, clean trend evidence, missing comparison evidence, and non-clean movement preservation.
- [x] Generate `.tmp/real-repo-benchmark-trend.json` and `.tmp/real-repo-benchmark-trend.md` from current benchmark comparison evidence.
- [x] Run targeted pytest and OpenSpec validation.
- [x] Run browser-style review of the generated Markdown evidence.
