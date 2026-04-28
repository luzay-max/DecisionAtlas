## 1. Current Quality Audit

- [x] 1.1 Audit current review decision payloads for source refs, artifact provenance, confidence, and extraction metadata already available to the web UI.
- [x] 1.2 Audit imported review card rendering to identify where strong, partial, and thin candidate evidence can be shown without adding a detail-page dependency.
- [x] 1.3 Audit benchmark fixtures and validation reports for current candidate-quality fields and gaps.
- [x] 1.4 Review current first-accepted-baseline guidance across dashboard, review, why, and drift entry points.

## 2. Candidate Quality Model

- [x] 2.1 Define a bounded candidate quality label derived from existing data such as grounded source-ref count, quote preview availability, provenance, and confidence.
- [x] 2.2 Add or expose candidate quality fields in API/read models without changing stored decision schema unless unavoidable.
- [x] 2.3 Preserve diagnostics for low-value or thin candidates without silently filtering them out of the review queue.

## 3. Review Product Surface

- [x] 3.1 Update imported review cards to show candidate quality label, source-ref strength, provenance, and confidence context compactly.
- [x] 3.2 Add clear copy for thin or low-value candidates so reviewers do not confuse them with strong baseline candidates.
- [x] 3.3 Ensure full detail links and existing accept/reject/supersede actions remain unchanged.
- [x] 3.4 Improve first accepted baseline guidance before and after acceptance without overstating downstream why/drift trust.

## 4. Real-Repo Quality Reporting

- [x] 4.1 Extend benchmark fixtures or validation report shape to capture candidate-quality expectations and observations.
- [x] 4.2 Update or create a real-repo decision-quality report recording candidate counts, strong/thin signal, provenance gaps, and follow-up risks.
- [x] 4.3 Keep live/provider-dependent quality observation outside default CI while preserving deterministic offline validation.

## 5. Tests

- [x] 5.1 Add or update engine/API tests for candidate quality field derivation and no-regression review payload shape.
- [x] 5.2 Add or update web tests for review card quality labels, provenance, confidence context, and thin-candidate copy.
- [x] 5.3 Add or update benchmark/report tests for candidate-quality fixture shape or report output.
- [x] 5.4 Run targeted tests covering review payloads, imported review UI, why/baseline guidance if touched, and benchmark validation.

## 6. Final Validation

- [x] 6.1 Run relevant typechecks for changed packages.
- [x] 6.2 Run OpenSpec validation for `improve-real-repo-decision-value-quality`.
- [x] 6.3 Record deferred extraction-pipeline or prompt-quality work discovered during implementation without expanding this change scope.
