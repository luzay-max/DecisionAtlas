## 1. Backend Readiness Summary

- [x] 1.1 Extend imported-workspace readiness output with richer descriptive fields and explicit recommended actions.
- [x] 1.2 Keep dashboard and why-answer context aligned on the same readiness semantics.
- [x] 1.3 Add backend regression coverage for review-ready, why-ready, evidence-limited, conversion-limited, and analysis-failed readiness payloads.

## 2. Product Surface

- [x] 2.1 Upgrade the imported readiness component to render richer readiness detail and multiple allowed next actions.
- [x] 2.2 Use the upgraded readiness surface consistently on dashboard and search pages.
- [x] 2.3 Keep wording clear about whether the workspace is ready for review, why, drift, or only summary inspection.

## 3. Validation

- [x] 3.1 Add or update web tests covering the richer imported readiness surface.
- [x] 3.2 Verify the dashboard and search flows still route correctly from the readiness actions.
- [x] 3.3 Run a quick imported-workspace smoke validation before closing the change.
