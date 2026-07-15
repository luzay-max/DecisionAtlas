# DecisionAtlas Team Handoff Report

- Label: `customer-host-trial`
- Generated at: `2026-07-15T13:45:00+08:00`
- Version: `customer-host-trial-2026-07-15`
- Commit: `b613033`
- Audience: `operator`
- Overall status: `warning`

## Workspace and Repository Scope

- Workspace: `github-hynek-structlog`
- Repository: `hynek/structlog`
- Provider: `github`
- Access mode: `public`
- Authorization status: `public`

## Evidence Status

| Evidence | Status | Summary |
| --- | --- | --- |
| benchmark_comparison | pass | {"comparison_type": "real-repo-benchmark-regression", "generated_at": "2026-07-15T05:21:29.801665+00:00", "improved": 0, "operationally_blocked": 0, "regressed": 0, "release_evidence_ready": true, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 5, "sparse_operationally_blocked": 0, "sparse_regressed": 0, "status": "pass"} |
| benchmark_trend | unknown | {"covered_repositories": 0, "generated_at": "2026-07-15T05:20:57.718440+00:00", "improved": 0, "label": null, "missing_from_current": 0, "missing_repositories": 0, "not_provided_repositories": 0, "operationally_blocked": 0, "operator_guided_repositories": 0, "recommended_follow_up": [], "regressed": 0, "repositories": 5, "sparse_improved": 0, "sparse_not_provided": 0, "sparse_operationally_blocked": 0, "sparse_regressed": 0, "status": "unknown"} |
| clean_install_rehearsal | warning | {"blocker_count": 0, "clean_package_path": ".tmp/clean-self-hosted-install/clean-self-hosted-install-rehearsal/package-copy", "clean_workspace_path": ".tmp/clean-self-hosted-install/clean-self-hosted-install-rehearsal", "evidence_family_statuses": {"benchmark_comparison": "not_provided", "external_install_evidence": "not_provided", "hosted_readiness": "not_provided", "license_support": "not_provided", "package_verification": "pass", "public_github_import": "not_provided", "readiness_history": "not_provided", "release_evidence": "not_provided", "team_handoff": "not_provided"}, "generated_at": "2026-07-15T05:03:22.219628+00:00", "label": "clean-self-hosted-install-rehearsal", "package_path": ".tmp/self-hosted-package/customer-host-trial", "recommended_next_actions": ["Review non-pass evidence lanes and either rerun with the missing input or disclose the operator-guided limitation.", "Archive clean install rehearsal evidence into readiness history before customer handoff."], "status": "warning", "warning_count": 9} |
| external_install_evidence | not_provided | {"status": "not_provided"} |
| hosted_readiness | operator_guided | {"blocker_count": 0, "generated_at": "2026-07-15T13:40:00+08:00", "known_limitation_count": 0, "lane_statuses": {"api_hosted_url": "operator_guided", "engine_hosted_url": "operator_guided", "governance_guardrail": "non_blocking", "hosted_health_check": "operator_guided", "hosted_smoke_check": "operator_guided", "real_repo_evidence": "pass", "recovery_drill": "warning", "release_evidence": "non_blocking", "seeded_demo_readiness": "operator_guided", "web_hosted_url": "operator_guided"}, "operator_guided_count": 6, "public_walkthrough_status": "operator_guided", "status": "operator_guided", "warning_count": 0} |
| license_support | not_provided | {"status": "not_provided"} |
| public_github_import | warning | {"benchmark_ready": null, "created_candidates": null, "full_extraction_requests": null, "import_status": null, "imported_count": null, "repository": null, "setup_outcome": null, "status": "warning", "workspace": null} |
| readiness_history | warning | {"entry_count": 18, "latest_counts": {"benchmark_improvements": 0, "benchmark_operational_blockers": 0, "benchmark_regressions": 0, "blockers": 0, "external_customer_host_v2_blockers": 0, "external_install_blockers": 0, "fresh_public_repo_import_blockers": 0, "full_chain_random_repo_release_blockers": 0, "known_limitations": 0, "not_provided": 1, "operator_guided": 2, "random_repo_warning_classified_lanes": 0, "random_repo_warning_external_dependency": 0, "random_repo_warning_product_controlled": 0, "real_continuity_blockers": 0, "real_external_host_trial_blockers": 0, "real_external_host_trial_placeholder_findings": 0, "warnings": 8}, "latest_entry_id": "2026-07-15-customer-host-trial-isolated", "latest_family_statuses": {"real_external_host_trial_evidence": "warning"}, "latest_label": "customer-host-trial-isolated", "status": "warning"} |
| real_continuity_rehearsal | warning | {"blocker_count": 0, "generated_at": "2026-07-15T05:03:22.415371+00:00", "label": "customer-host-trial-continuity", "lane_statuses": {"database_backup": "pass", "path_safety:backup_artifact": "pass", "path_safety:rehearsal_dir": "pass", "path_safety:restore_state": "pass", "path_safety:source_state": "pass", "post_upgrade_validation": "operator_guided", "redaction": "pass", "restore_validation": "pass", "rollback_plan": "operator_guided", "scratch_workspace": "pass", "upgrade_transition": "pass"}, "recommended_next_actions": ["Review operator-guided continuity lanes and attach post-upgrade smoke evidence before customer handoff.", "Archive real continuity evidence into readiness history when making durable self-hosted claims."], "redaction_finding_count": 0, "restore_matches_source": true, "restored_record_count": 2, "scratch_only": true, "source_record_count": 2, "status": "warning"} |
| release_evidence | warning | {"advisory_signals": [{"id": "governance_guardrail", "label": "Governance guardrail", "status": "warning"}, {"id": "targeted_tests", "label": "Targeted test summary", "status": "pass"}, {"id": "real_repo_benchmark_comparison", "label": "Real-repo benchmark comparison", "status": "pass"}, {"id": "trend_comparison", "label": "Release trend comparison", "status": "pass"}], "generated_at": "2026-07-15T13:35:00+08:00", "missing_input_count": 0, "required_gates": [{"id": "canonical_pre_release", "label": "Canonical pre-release baseline", "status": "pass"}, {"id": "openspec_strict_validation", "label": "OpenSpec strict validation", "status": "pass"}, {"id": "offline_benchmark_validation", "label": "Offline benchmark fixture validation", "status": "pass"}], "status": "warning", "warning_count": 0} |
| review_audit | not_provided | {"status": "not_provided"} |
| self_hosted_package | pass | {"blocker_count": 0, "checked_file_count": 59, "generated_at": "2026-07-15T05:03:21.959919+00:00", "non_pass_lanes": [{"id": "runtime_smoke", "label": "Runtime smoke", "reason": "Package verifier is offline; run real-stack smoke separately.", "status": "operator_guided"}, {"id": "private_repository_token_validation", "label": "Private repository token validation", "reason": "Customer token must remain on operator-controlled host and is not included in the package.", "status": "operator_guided"}, {"id": "private_repo_pilot_evidence", "label": "Private repo pilot evidence", "reason": "Package includes the sanitized template and verifier; actual private-repo proof must be generated on the customer-controlled host.", "status": "operator_guided"}, {"id": "live_benchmark", "label": "Live public repository benchmark", "reason": "Run public GitHub import rehearsal and benchmark comparison separately before claiming this lane.", "status": "not_provided"}, {"id": "readiness_history", "label": "Readiness evidence history", "reason": "Archive generated evidence into docs/evidence/readiness separately.", "status": "not_provided"}, {"id": "clean_self_hosted_install_rehearsal", "label": "Clean self-hosted install rehearsal", "reason": "Run rehearse_clean_self_hosted_install.py separately before claiming external operator trial readiness.", "status": "not_provided"}, {"id": "backup_restore_upgrade_rehearsal", "label": "Backup restore upgrade rehearsal", "reason": "Run rehearse_backup_restore_upgrade.py and attach continuity evidence before clean long-term self-hosted operation claims.", "status": "not_provided"}, {"id": "real_backup_restore_upgrade_rehearsal", "label": "Real backup restore upgrade rehearsal", "reason": "Run rehearse_real_backup_restore_upgrade.py in scratch mode before claiming tested backup/restore/upgrade mechanics.", "status": "not_provided"}, {"id": "external_self_hosted_install_evidence", "label": "External self-hosted install evidence", "reason": "Run collect_external_self_hosted_install_evidence.py with operator-filled evidence from a clean VM or customer-controlled host before claiming customer-host proof.", "status": "not_provided"}, {"id": "pilot_customer_delivery_kit", "label": "Pilot customer delivery kit", "reason": "Run verify_pilot_customer_delivery_kit.py and attach customer-readable pilot materials before external evaluation.", "status": "not_provided"}, {"id": "pilot_commercial_proposal_kit", "label": "Pilot commercial proposal kit", "reason": "Run verify_pilot_commercial_proposal_kit.py and attach proposal, quote assumptions, acceptance, support, renewal, and upgrade materials before paid pilot outreach.", "status": "not_provided"}, {"id": "commercial_sales_enablement_kit", "label": "Commercial sales enablement kit", "reason": "Package includes sales page, one-page brief, and use-case materials; attach reviewed buyer-facing versions before paid outreach.", "status": "not_provided"}, {"id": "team_handoff_report", "label": "Team handoff report", "reason": "Generate JSON/Markdown handoff evidence after release, readiness, benchmark, and package evidence are available.", "status": "not_provided"}, {"id": "license_support_boundary", "label": "License and support boundary", "reason": "Package includes boundary docs and an entitlement template; attach customer-specific entitlement separately for paid handoff.", "status": "operator_guided"}], "package_label": "customer-host-trial", "status": "pass", "version_label": "customer-host-trial-2026-07-15"} |
| trend_comparison | not_provided | {"status": "not_provided"} |

## Review and Audit Activity

- No audit history source was provided.

## Source Evidence

| Source | Status | Path | Warnings |
| --- | --- | --- | --- |
| Benchmark comparison | pass | .tmp/customer-host-trial-benchmark-comparison.json | [] |
| Benchmark trend evidence | pass | .tmp/customer-host-trial-benchmark-snapshot.json | [] |
| Clean self-hosted install rehearsal | pass | .tmp/customer-host-trial-clean-install.json | [] |
| External self-hosted install evidence | not_provided | - | ["source_not_provided"] |
| Hosted/operator readiness | pass | .tmp/customer-host-trial-hosted-readiness.json | [] |
| License and support boundary | not_provided | - | ["source_not_provided"] |
| Public GitHub import rehearsal | pass | .tmp/customer-host-trial-fresh-repo.json | [] |
| Readiness evidence history | pass | docs/evidence/readiness/index.json | [] |
| Real backup/restore/upgrade rehearsal | pass | .tmp/customer-host-trial-real-continuity.json | [] |
| Release evidence | pass | .tmp/customer-host-trial-release-evidence.json | [] |
| Review audit history | not_provided | - | ["source_not_provided"] |
| Self-hosted package verification | pass | .tmp/customer-host-trial-package-verification.json | [] |
| Release trend comparison | not_provided | - | ["source_not_provided"] |

## Limitations and Next Actions

- This report is a bounded handoff snapshot, not a live dashboard.
- Missing, operator-guided, known-limitation, warning, and blocking states are preserved.
- Local clean install rehearsal is not customer-host proof unless external install evidence is supplied.
- Non-destructive continuity verifier evidence is not real backup/restore/upgrade proof unless real continuity rehearsal evidence is supplied.
- Secrets, raw tokens, private repository dumps, and unbounded local-only paths are excluded.
- Resolve or explicitly accept non-clean evidence states before using this as a clean customer handoff.
