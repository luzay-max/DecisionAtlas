from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_script(name: str):
    root = Path(__file__).resolve().parents[4]
    module_path = root / "scripts" / "ci" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _scratch_dir(name: str) -> Path:
    root = Path(__file__).resolve().parents[4]
    path = root / ".tmp" / "ci-test-scratch" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_self_hosted_package_builder_writes_manifest_and_allowlisted_assets() -> None:
    builder = _load_script("build_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    output_root = _scratch_dir("package-builder")

    manifest = builder.build_package(
        root=root,
        output_root=output_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = output_root / "decisionatlas-self-hosted-test"
    manifest_path = package_dir / "manifest.json"
    readme_path = package_dir / "README.md"

    assert manifest["package_label"] == "decisionatlas-self-hosted-test"
    assert manifest["commit"] == "abc123"
    assert manifest_path.exists()
    assert readme_path.exists()
    assert "DecisionAtlas Self-Hosted Package" in readme_path.read_text(encoding="utf-8")
    assert (package_dir / "templates" / "self-hosted.env.example").exists()
    assert (package_dir / "templates" / "self-hosted-entitlement.example.json").exists()
    assert (package_dir / "docs" / "project" / "self-hosted-package-guide.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-customer-delivery-kit.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-delivery-email-template.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-commercial-proposal-kit.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-paid-quote-template.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-acceptance-checklist.md").exists()
    assert (package_dir / "docs" / "project" / "pilot-support-renewal-upgrade-boundary.md").exists()
    assert (package_dir / "docs" / "project" / "commercial-sales-page-draft.md").exists()
    assert (package_dir / "docs" / "project" / "commercial-one-page-brief.md").exists()
    assert (package_dir / "docs" / "project" / "commercial-use-cases.md").exists()
    assert (package_dir / "docs" / "project" / "private-repo-pilot-evidence-template.md").exists()
    assert (package_dir / "docs" / "project" / "private-repo-pilot-evidence-example.md").exists()
    assert (package_dir / "docs" / "project" / "backup-restore-upgrade-rehearsal.md").exists()
    assert (package_dir / "docs" / "project" / "self-hosted-license-and-support-boundary.md").exists()
    assert (package_dir / "scripts" / "ci" / "verify_pilot_customer_delivery_kit.py").exists()
    assert (package_dir / "scripts" / "ci" / "verify_pilot_commercial_proposal_kit.py").exists()
    assert (package_dir / "scripts" / "ci" / "verify_private_repo_pilot_evidence.py").exists()
    assert (package_dir / "scripts" / "ci" / "rehearse_backup_restore_upgrade.py").exists()
    assert (package_dir / "scripts" / "ci" / "rehearse_real_backup_restore_upgrade.py").exists()
    assert (package_dir / "scripts" / "dev" / "start-real-stack.ps1").exists()
    assert (package_dir / "templates" / "private-repo-pilot-evidence.example.json").exists()
    assert (package_dir / "templates" / "backup-restore-upgrade-rehearsal.example.json").exists()
    assert (package_dir / "templates" / "external-self-hosted-install-evidence.example.json").exists()
    assert (package_dir / "templates" / "customer-host-trial.example.json").exists()
    assert (package_dir / "docs" / "project" / "external-self-hosted-install-evidence.md").exists()
    assert (package_dir / "scripts" / "ci" / "collect_external_self_hosted_install_evidence.py").exists()
    assert (package_dir / "scripts" / "ci" / "collect_real_external_host_trial_evidence.py").exists()
    assert (package_dir / "scripts" / "ci" / "rehearse_runnable_self_hosted_package.py").exists()
    assert (package_dir / "package.json").exists()
    assert (package_dir / "pnpm-lock.yaml").exists()
    assert (package_dir / "pnpm-workspace.yaml").exists()
    assert (package_dir / "docker-compose.yml").exists()
    assert (package_dir / "apps" / "web" / "tests-e2e" / "imported-workspace-core-loop.spec.ts").exists()
    assert (package_dir / "apps" / "api" / "src" / "server.ts").exists()
    assert (package_dir / "services" / "engine" / "app" / "main.py").exists()
    assert (package_dir / "services" / "engine" / "alembic" / "env.py").exists()
    assert (package_dir / "packages" / "prompts" / "decision-screening.md").exists()
    assert (package_dir / "infra" / "docker" / "redis" / "redis.conf").exists()
    assert "--project-name $composeProjectName" in (
        package_dir / "scripts" / "dev" / "start-real-stack.ps1"
    ).read_text(encoding="utf-8")
    assert "--project-name $composeProjectName" in (
        package_dir / "scripts" / "dev" / "stop-real-stack.ps1"
    ).read_text(encoding="utf-8")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2
    assert data["version_label"] == "test-version"
    assert data["runtime"]["package_type"] == "runnable_source_tree_handoff"
    assert data["runtime"]["dependency_install_commands"] == [
        "pnpm install --frozen-lockfile",
        "uv sync --project services/engine --frozen",
    ]
    assert "--install-browser" in data["runtime"]["smoke_command"]
    assert data["runtime"]["customer_controlled_host_proof"] == "requires_separate_sanitized_external_evidence"
    assert "runtime_license_enforcement" in data["unsupported_capabilities"]
    assert "offline_entitlement_template" in data["readiness_evidence_expectations"]
    assert "pilot_customer_delivery_kit_verification_json" in data["readiness_evidence_expectations"]
    assert "pilot_commercial_proposal_kit_verification_json" in data["readiness_evidence_expectations"]
    assert "private_repo_pilot_evidence_template" in data["readiness_evidence_expectations"]
    assert "private_repo_pilot_evidence_verification_json" in data["readiness_evidence_expectations"]
    assert "backup_restore_upgrade_rehearsal_json" in data["readiness_evidence_expectations"]
    assert "real_backup_restore_upgrade_rehearsal_json" in data["readiness_evidence_expectations"]
    assert "external_self_hosted_install_evidence_json" in data["readiness_evidence_expectations"]
    assert "commercial_sales_enablement_kit" in data["readiness_evidence_expectations"]
    assert "python scripts\\ci\\verify_self_hosted_package.py --package <package-path>" in data["validation_commands"]
    assert any("rehearse_clean_self_hosted_install.py" in command for command in data["validation_commands"])
    assert any("rehearse_backup_restore_upgrade.py" in command for command in data["validation_commands"])
    assert any("verify_pilot_customer_delivery_kit.py" in command for command in data["validation_commands"])
    assert any("verify_pilot_commercial_proposal_kit.py" in command for command in data["validation_commands"])


def test_self_hosted_package_verifier_passes_valid_package() -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    output_root = _scratch_dir("package-verifier-valid")
    builder.build_package(
        root=root,
        output_root=output_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = output_root / "decisionatlas-self-hosted-test"
    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")
    markdown = verifier.render_markdown(bundle)

    assert bundle["status"] == "pass"
    assert bundle["blockers"] == []
    assert bundle["checked_file_count"] > 10
    assert {lane["id"] for lane in bundle["non_pass_lanes"]} == {
        "runtime_smoke",
        "private_repository_token_validation",
        "private_repo_pilot_evidence",
        "live_benchmark",
        "readiness_history",
        "clean_self_hosted_install_rehearsal",
        "backup_restore_upgrade_rehearsal",
        "real_backup_restore_upgrade_rehearsal",
        "external_self_hosted_install_evidence",
        "pilot_customer_delivery_kit",
        "pilot_commercial_proposal_kit",
        "commercial_sales_enablement_kit",
        "team_handoff_report",
        "license_support_boundary",
    }
    assert "Runtime smoke" in markdown
    assert "operator_guided" in markdown
    assert "not_provided" in markdown


def test_self_hosted_package_verifier_blocks_missing_required_file() -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    output_root = _scratch_dir("package-verifier-missing-file")
    builder.build_package(
        root=root,
        output_root=output_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = output_root / "decisionatlas-self-hosted-test"
    (package_dir / "scripts" / "dev" / "start-real-stack.ps1").unlink()

    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(
        blocker["id"] == "file:scripts/dev/start-real-stack.ps1"
        for blocker in bundle["blockers"]
    )


def test_self_hosted_package_verifier_blocks_secret_like_files() -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    output_root = _scratch_dir("package-verifier-secret-file")
    builder.build_package(
        root=root,
        output_root=output_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = output_root / "decisionatlas-self-hosted-test"
    (package_dir / ".env").write_text("LLM_API_KEY=secret", encoding="utf-8")

    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")

    assert bundle["status"] == "blocking"
    assert any(blocker["id"] == "secret_exclusions" for blocker in bundle["blockers"])


def test_runtime_copy_filter_excludes_local_state_and_build_outputs() -> None:
    builder = _load_script("build_self_hosted_package")

    for relative in (
        Path("apps/web/node_modules/pkg/index.js"),
        Path("apps/web/.next/server.js"),
        Path("services/engine/.venv/pyvenv.cfg"),
        Path("services/engine/app/__pycache__/main.pyc"),
        Path("apps/api/.env.local"),
        Path("apps/api/runtime.log"),
        Path("services/engine/local.sqlite"),
    ):
        assert builder._is_excluded_runtime_path(relative)

    assert not builder._is_excluded_runtime_path(Path("apps/web/app/page.tsx"))


def test_self_hosted_package_verifier_blocks_legacy_doc_only_package() -> None:
    builder = _load_script("build_self_hosted_package")
    verifier = _load_script("verify_self_hosted_package")
    root = Path(__file__).resolve().parents[4]
    output_root = _scratch_dir("package-verifier-legacy-doc-only")
    builder.build_package(
        root=root,
        output_root=output_root,
        package_label="decisionatlas-self-hosted-test",
        version_label="test-version",
        commit="abc123",
        generated_at="2026-06-08T00:00:00+00:00",
    )

    package_dir = output_root / "decisionatlas-self-hosted-test"
    manifest_path = package_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("runtime")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (package_dir / "package.json").unlink()

    bundle = verifier.verify_package(package_dir, generated_at="2026-06-08T00:00:00+00:00")
    blocker_ids = {blocker["id"] for blocker in bundle["blockers"]}

    assert bundle["status"] == "blocking"
    assert bundle["runnable_status"] == "blocking"
    assert "manifest_field:runtime" in blocker_ids
    assert "file:package.json" in blocker_ids
