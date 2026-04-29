## 1. Candidate Quality Model

- [x] 1.1 Review the current `candidate_quality` payload and confirm which fields already satisfy the new specs.
- [x] 1.2 Tighten the deterministic `strong`, `partial`, and `thin` label rules so high confidence alone cannot promote weak evidence.
- [x] 1.3 Add bounded reason categories for missing or limited support, including missing source refs, missing previewable quotes, missing provenance, missing source URL, and low confidence.
- [x] 1.4 Add engine/API tests for strong, partial, thin, and high-confidence-but-weak-evidence boundary cases.

## 2. Review Product Surface

- [x] 2.1 Update imported review card rendering to make partial-candidate limitations as clear as thin-candidate limitations.
- [x] 2.2 Update English and Chinese review copy for calibrated quality labels and reason guidance.
- [x] 2.3 Add or update web tests covering strong, partial, thin, and high-confidence weak-evidence review cards.

## 3. Real-Repository Quality Reporting

- [x] 3.1 Update benchmark/report output to include quality label distribution, thin pressure, provenance gaps, previewable source-ref count, and bounded reason counts.
- [x] 3.2 Adjust deterministic fixture expectations only where stricter labels require it.
- [x] 3.3 Add or update benchmark validation tests for the new candidate-quality report shape.

## 4. Documentation And Validation

- [x] 4.1 Update `docs/project/real-repo-decision-quality-report.md` with the calibrated model and current limitations.
- [x] 4.2 Run targeted engine/API, web review, and benchmark tests.
- [x] 4.3 Run `openspec validate improve-real-repo-decision-signal-quality --type change --strict`.
- [x] 4.4 Run the appropriate broader validation command if targeted tests indicate release-risk changes.
