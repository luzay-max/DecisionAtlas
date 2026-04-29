## 1. Baseline Verification

- [x] 1.1 Confirm working tree scope and include the new master plan in the intended release baseline.
- [x] 1.2 Confirm no existing local or remote `v0.3.0-rc.1` tag is present before tagging.
- [x] 1.3 Run `openspec validate --all --strict` and record the result.
- [x] 1.4 Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1` and record the result.

## 2. Release Documentation Alignment

- [x] 2.1 Update English v0.3 RC release notes with the final validated commit, validation timestamp, and tag status.
- [x] 2.2 Update Chinese v0.3 RC release notes with the same final validated commit, validation timestamp, and tag status.
- [x] 2.3 Update the release checklist or update log with the final validation and tag evidence.
- [x] 2.4 Ensure hosted preview and real-stack checks remain described as confidence layers rather than mandatory release gates.

## 3. Commit, Tag, And Push

- [ ] 3.1 Commit the master plan, OpenSpec artifacts, and release documentation updates.
- [ ] 3.2 Verify the final release commit hash after the release commit is created.
- [ ] 3.3 Create local tag `v0.3.0-rc.1` on the final release commit.
- [ ] 3.4 Push the release commit and tag to `origin`.
- [ ] 3.5 Verify local and remote tag state after push.

## 4. Final Checks

- [ ] 4.1 Re-check `git status --short --branch` to confirm the branch is clean and synced.
- [ ] 4.2 Record any environment-dependent checks that remain known limitations rather than release blockers.
