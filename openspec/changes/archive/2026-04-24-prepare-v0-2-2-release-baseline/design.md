## Context

The current branch has moved beyond the earlier `v0.2.1` baseline. The product now has a canonical local release gate, repaired Playwright smoke coverage, improved imported candidate conversion, first-accepted-baseline readiness semantics, stronger benchmark fixtures, and separated English/Chinese documentation. The README still describes the project stage as core MVP and v0.2 demo hardening, so the public project narrative is behind the code and specs.

This change is intentionally release-facing. It should not change extraction, retrieval, drift, auth, or import behavior unless validation exposes a real release-blocking mismatch. The main output is a coherent `v0.2.2` baseline: documentation, release notes, validation evidence, and tag readiness.

## Goals / Non-Goals

**Goals:**

- Align release-facing documentation with the current imported-readiness baseline.
- Add `v0.2.2` release notes with shipped capabilities, validation commands, scope, and limitations.
- Ensure English and Chinese docs agree on current stage, stable demo lane, imported lane, and known limitations.
- Run and record the canonical `scripts/ci/pre-release.ps1` validation path.
- Prepare a clean `v0.2.2` tag point once validation passes.

**Non-Goals:**

- No extraction, why-search, drift, review, auth, or import behavior changes.
- No hosted demo deployment work.
- No GitHub App onboarding, private repo productization, or login/scope UI.
- No expansion of live real-repo validation beyond documenting the current optional operator-guided layer.

## Decisions

### 1. Treat `pre-release.ps1` as the only required release gate

The release checklist and release notes will point to the canonical PowerShell gate instead of listing a separate required command set. Individual test commands remain useful for debugging, but the release milestone should have one source of truth.

Alternative considered:
- Re-list every test command in the release notes.

Why not:
- It invites drift from the canonical script and makes future release changes harder to keep consistent.

### 2. Keep live real-repo checks optional for `v0.2.2`

`v0.2.2` should record that live real-repo smoke checks are valuable but not required for the default release gate. The current default path already validates offline fixtures and Playwright smoke coverage; live provider/network checks are better handled by the next `stabilize-live-real-repo-validation` change.

Alternative considered:
- Make `--live-real-repos` part of the `v0.2.2` release gate.

Why not:
- It would make the release baseline depend on provider credentials, network state, and pre-existing imported workspaces.

### 3. Update project stage wording, not product scope

The README stage line should move from `Core MVP & v0.2 Demo Hardening Complete` to a more accurate post-`v0.2.1` release-baseline description. The limitation section should still say auth/multi-user and full GitHub App/private repo productization are not complete.

Alternative considered:
- Reframe the project as v0.3-ready in README.

Why not:
- Backend/spec foundations exist, but productized platform flows are still deferred.

## Risks / Trade-offs

- [Risk] Release notes overstate current imported-lane maturity.
  Mitigation: keep limitations explicit and separate offline release validation from optional live confidence checks.

- [Risk] English and Chinese docs drift again.
  Mitigation: update paired docs in the same change and keep the same stage wording and limitation categories.

- [Risk] Tag readiness is confused with creating/pushing the tag during implementation.
  Mitigation: tasks should prepare and verify the tag target; the final tag push can be an explicit release step after validation.

## Migration Plan

1. Update release-facing docs and add `v0.2.2` release notes.
2. Run the canonical release gate.
3. Record validation evidence in release notes or release checklist.
4. Confirm the tree is clean and identify the intended `v0.2.2` tag commit.
5. Create and push the tag only after validation and user confirmation.

Rollback is documentation-only unless a release-blocking validation mismatch requires a small script fix. If release notes or stage wording prove inaccurate, revert the doc changes and keep the current `main` behavior unchanged.

## Open Questions

- Should the implementation create and push the `v0.2.2` tag automatically after validation, or stop at tag readiness and wait for explicit release confirmation?
- Should the new release notes be English-only like `release-notes-v0.2.md`, or should this change also add a Chinese release note mirror?
