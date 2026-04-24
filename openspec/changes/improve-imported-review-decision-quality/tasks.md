## 1. Backend review evidence model

- [ ] 1.1 Extend decision list serialization with optional review evidence fields: source-ref count, preview quotes, artifact summary, and workspace mode/provenance where available.
- [ ] 1.2 Keep detail endpoint behavior compatible while sharing the same compact source-ref serialization helpers.
- [ ] 1.3 Add backend API tests for imported candidate list evidence, artifact provenance, and thin/no source-ref fallback.

## 2. Frontend review queue quality

- [ ] 2.1 Extend web API types for review evidence, artifact provenance, and imported review metadata.
- [ ] 2.2 Update imported review page guidance to explain first accepted baseline and downstream why/drift implications.
- [ ] 2.3 Update review candidate cards to show evidence preview, source-ref count, artifact provenance, confidence context, and detail-page link without changing review actions.
- [ ] 2.4 Preserve guided demo review behavior and avoid cluttering demo cards with imported-only guidance.

## 3. Validation and documentation

- [ ] 3.1 Add or update frontend tests covering imported review evidence cards and demo-lane stability.
- [ ] 3.2 Run targeted backend and frontend review tests.
- [ ] 3.3 Run the default offline benchmark validation to ensure release baseline fixtures remain unaffected.
- [ ] 3.4 Update project documentation if the review workflow wording changes materially.
