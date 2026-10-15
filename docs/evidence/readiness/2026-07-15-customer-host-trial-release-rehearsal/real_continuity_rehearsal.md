# Real Backup Restore Upgrade Rehearsal

- Label: `customer-host-trial-continuity`
- Generated at: `2026-07-15T05:03:22.415371+00:00`
- Status: `warning`
- Scratch only: `True`
- Rehearsal dir: `.tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity`

## Restore Integrity

- Source SHA256: `491b498f0c857847f282bf4175c00e4f4805aabd145af0d408a95721f0e3a00b`
- Restored SHA256: `491b498f0c857847f282bf4175c00e4f4805aabd145af0d408a95721f0e3a00b`
- Restore matches source: `True`
- Source records: `2`
- Restored records: `2`

## Continuity Lanes

| Lane | Status | Details |
| --- | --- | --- |
| Scratch workspace | pass | {"path": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity"} |
| Scratch state backup | pass | {"backup_artifact": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity/backup/state-backup.json", "source_sha256": "491b498f0c857847f282bf4175c00e4f4805aabd145af0d408a95721f0e3a00b"} |
| Scratch restore validation | pass | {"matches_source": true, "restored_sha256": "491b498f0c857847f282bf4175c00e4f4805aabd145af0d408a95721f0e3a00b", "restored_state": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity/restore/state.json"} |
| Upgrade transition metadata | pass | {"previous_version": "customer-host-trial-before", "target_version": "customer-host-trial-2026-07-15"} |
| Post-upgrade validation | operator_guided | {"status_source": "argument"} |
| Rollback plan | operator_guided | {"status_source": "argument"} |
| rehearsal_dir path stays inside owned scratch root | pass | {"path": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity", "scratch_root": ".tmp/real-backup-restore-upgrade-rehearsal"} |
| source_state path stays inside owned scratch root | pass | {"path": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity/source/state.json", "scratch_root": ".tmp/real-backup-restore-upgrade-rehearsal"} |
| backup_artifact path stays inside owned scratch root | pass | {"path": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity/backup/state-backup.json", "scratch_root": ".tmp/real-backup-restore-upgrade-rehearsal"} |
| restore_state path stays inside owned scratch root | pass | {"path": ".tmp/real-backup-restore-upgrade-rehearsal/customer-host-trial-continuity/restore/state.json", "scratch_root": ".tmp/real-backup-restore-upgrade-rehearsal"} |
| Sensitive material scan | pass | {"finding_count": 0} |

## Limitations

- This rehearsal proves backup/restore mechanics only for explicit scratch state, not production customer data.
- Raw database dumps, .env files, provider keys, repository tokens, and private repository content remain outside generated evidence.
- Full Web/API/Engine post-upgrade smoke must be attached separately when customer-facing upgrade readiness is claimed.

## Recommended Next Actions

- Review operator-guided continuity lanes and attach post-upgrade smoke evidence before customer handoff.
- Archive real continuity evidence into readiness history when making durable self-hosted claims.
