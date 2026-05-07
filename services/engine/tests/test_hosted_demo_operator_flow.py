from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def read_repo_file(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_hosted_demo_operator_scripts_are_present_and_bounded() -> None:
    expected_scripts = [
        "scripts/demo/health-check.ps1",
        "scripts/demo/smoke-check.ps1",
        "scripts/demo/reset-demo.ps1",
        "scripts/demo/reseed-demo.ps1",
        "scripts/demo/reset_seeded_demo.py",
        "scripts/demo/check_seeded_demo.py",
    ]

    for relative_path in expected_scripts:
        assert (REPO_ROOT / relative_path).exists(), relative_path

    reset_script = read_repo_file("scripts/demo/reset-demo.ps1")
    reset_helper = read_repo_file("scripts/demo/reset_seeded_demo.py")

    assert "Imported workspaces are not deleted by this script." in reset_script
    assert "check_seeded_demo.py" in reset_script
    assert 'DEMO_WORKSPACE_SLUG = "demo-workspace"' in reset_helper
    assert "Workspace.slug == DEMO_WORKSPACE_SLUG" in reset_helper


def test_hosted_demo_docs_reference_canonical_operator_commands() -> None:
    guide = read_repo_file("docs/project/hosted-demo-operator-guide.md")
    guide_zh = read_repo_file("docs/project/hosted-demo-operator-guide_zh-CN.md")
    deployment = read_repo_file("docs/project/deployment.md")
    quick_start = read_repo_file("docs/project/quick-start.md")

    for content in [guide, guide_zh, deployment, quick_start]:
        assert "scripts\\demo\\health-check.ps1" in content
        assert "scripts\\demo\\smoke-check.ps1" in content

    assert "scripts\\demo\\reset-demo.ps1" in guide
    assert "scripts\\demo\\reseed-demo.ps1" in guide
    assert "python scripts\\demo\\check_seeded_demo.py" in guide
    assert "Imported workspaces are not deleted" in guide
    assert "导入工作区不会被删除" in guide_zh


def test_real_stack_startup_documents_explicit_seeded_demo_reset() -> None:
    start_script = read_repo_file("scripts/dev/start-real-stack.ps1")
    start_bat = read_repo_file("scripts/dev/start-real-stack.bat")
    quick_start = read_repo_file("docs/project/quick-start.md")
    deployment = read_repo_file("docs/project/deployment.md")

    assert "[switch]$ResetSeededDemo" in start_script
    assert "check_seeded_demo.py --no-fail" in start_script
    assert "%*" in start_bat
    assert "-ResetSeededDemo" in quick_start
    assert "-ResetSeededDemo" in deployment


def test_playwright_config_supports_hosted_smoke_mode() -> None:
    config = read_repo_file("apps/web/playwright.config.ts")
    smoke_script = read_repo_file("scripts/demo/smoke-check.ps1")

    assert "PLAYWRIGHT_BASE_URL" in config
    assert "PLAYWRIGHT_SKIP_WEBSERVER" in config
    assert "skipWebServer ? undefined" in config
    assert "$env:PLAYWRIGHT_SKIP_WEBSERVER = \"1\"" in smoke_script
    assert "$env:PLAYWRIGHT_BASE_URL" in smoke_script
