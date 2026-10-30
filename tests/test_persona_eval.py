import json
import subprocess
from pathlib import Path

import pytest

from bobp.tools import persona_eval


def test_load_catalog_requires_unique_suites_and_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    suite = {
        "id": "bob-persona-authoring",
        "persona": "bob",
        "request": "Create a persona skill.",
        "artifact": "agents/example/SKILL.md",
        "rubric": "agents/templates/_template_PERSONA_SKILL.md",
    }
    path.write_text(json.dumps({"version": 1, "suites": [suite]}))

    assert persona_eval.load_catalog(path) == [suite]

    path.write_text(json.dumps({"version": 2, "suites": [suite]}))
    with pytest.raises(ValueError, match="version 1"):
        persona_eval.load_catalog(path)

    path.write_text(json.dumps({"version": 1, "suites": [suite, suite]}))
    with pytest.raises(ValueError, match="Duplicate eval suite id"):
        persona_eval.load_catalog(path)


def test_repository_catalog_has_matching_persona_suites() -> None:
    suites = persona_eval.load_catalog()

    assert {suite["id"] for suite in suites} == {
        "bob-persona-authoring",
        "morpheus-design-advice",
        "cypher-personality",
        "morpheus-personality",
        "mouse-personality",
        "neo-personality",
        "oracle-personality",
        "smith-personality",
        "tank-personality",
        "trin-personality",
    }
    morpheus = next(suite for suite in suites if suite["persona"] == "morpheus")
    assert morpheus["artifact"] == "docs/decisions/ADR-0001-refund-lifecycle.md"
    assert morpheus["rubric"] == "agents/templates/_template_DECISION.md"


def test_project_root_does_not_require_bobp_checkout_or_makefile(tmp_path: Path) -> None:
    project = tmp_path / "customer-project"
    nested = project / "src"
    nested.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\nname='customer'\n")

    assert persona_eval.find_project_root(nested) == project


def test_catalog_paths_cannot_escape_disposable_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    assert persona_eval._project_path(project, "agents/new/SKILL.md") == project / "agents/new/SKILL.md"
    with pytest.raises(ValueError, match="escapes project"):
        persona_eval._project_path(project, "../outside.md")


def test_extract_rubric_returns_embedded_persona_checklist() -> None:
    template = "Before\n<!-- RUBRIC-START -->\n## Check\n- [ ] Clear purpose\n<!-- RUBRIC-END -->\nAfter"

    assert persona_eval.extract_rubric(template) == "## Check\n- [ ] Clear purpose"

    with pytest.raises(ValueError, match="RUBRIC-START"):
        persona_eval.extract_rubric("no rubric markers")


def test_prepare_test_project_runs_local_bobp_install_in_isolated_locations(
    tmp_path: Path,
) -> None:
    root = persona_eval.find_project_root()
    temp_root = tmp_path / "runner"
    temp_root.mkdir()
    project = tmp_path / "project"

    persona_eval.prepare_test_project(project, temp_root)

    assert (project / "README.md").is_file()
    assert (project / "pyproject.toml").is_file()
    assert (project / "agents/bob/SKILL.md").read_text() == (
        root / "bobp/templates/agents/bob/SKILL.md.txt"
    ).read_text()
    assert (project / "agents/morpheus/SKILL.md").read_text() == (
        root / "bobp/templates/agents/morpheus/SKILL.md.txt"
    ).read_text()
    assert (project / "agents/templates/_template_PERSONA_SKILL.md").is_file()
    installed_decision_template = project / "agents/templates/_template_DECISION.md"
    assert installed_decision_template.read_text() == (
        root / "bobp/templates/agents/templates/_template_DECISION.md"
    ).read_text()
    assert (project / ".agents/skills/bob").is_symlink()
    assert (project / ".agents/skills/bob/SKILL.md").is_file()
    assert (project / ".agents/skills/morpheus/SKILL.md").is_file()
    assert (temp_root / "codex-home/skills/bob").is_symlink()


def test_setup_prints_global_npm_instructions_without_installing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def which(name: str) -> str | None:
        return f"/{name}" if name in {"node", "npm"} else None

    monkeypatch.setattr(persona_eval.shutil, "which", which)
    monkeypatch.setattr(
        persona_eval.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, returncode=0, stdout="v24.15.0\n", stderr=""),
    )

    assert persona_eval.show_node_setup_instructions() == 0

    # Setup is informational only and never writes packages or files into the project.
    assert not (tmp_path / "build").exists()


def test_global_runtime_error_lists_exact_install_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modules = tmp_path / "node_modules"
    modules.mkdir()
    monkeypatch.setattr(
        persona_eval.shutil,
        "which",
        lambda name: f"/{name}" if name in {"node", "npm"} else None,
    )

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, returncode=0, stdout="v24.15.0\n" if args[1:] == ["--version"] else f"{modules}\n", stderr="")

    monkeypatch.setattr(persona_eval.subprocess, "run", run)

    error = persona_eval._global_node_runtime_error()

    assert error is not None
    assert "promptfoo@0.125.1" in error
    assert "@openai/codex-sdk@0.156.1" in error


def test_node_prerequisite_error_explains_missing_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(persona_eval.shutil, "which", lambda name: None)

    error = persona_eval.check_node_prerequisites()

    assert error is not None
    assert "Node.js >=22.22.0 and npm" in error
    assert "https://nodejs.org/" in error


def test_node_prerequisite_error_reports_unsupported_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        persona_eval.shutil, "which", lambda name: f"/{name}" if name in {"node", "npm"} else None
    )
    monkeypatch.setattr(
        persona_eval.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, returncode=0, stdout="v20.12.0\n", stderr=""
        ),
    )

    assert persona_eval.check_node_prerequisites() == (
        "persona-eval requires Node.js >=22.22.0; found v20.12.0. Upgrade Node.js and retry."
    )


def test_build_config_checks_skill_use_and_artifact_rubric(tmp_path: Path) -> None:
    suite = {
        "id": "bob-persona-authoring",
        "persona": "bob",
        "request": "Create a persona skill.",
        "artifact": "agents/example/SKILL.md",
        "rubric": "agents/templates/_template_PERSONA_SKILL.md",
    }

    fixture_capabilities = "# Project capabilities\n\nvia: disabled\n"
    config = persona_eval.build_config(
        suite, tmp_path, "## Check\n- [ ] Clear purpose", fixture_capabilities
    )
    provider = config["providers"][0]["config"]
    checks = config["tests"][0]["assert"]

    assert "Create a persona skill." in config["prompts"][0]
    assert provider["model"] == "gpt-6-luna"
    assert provider["sandbox_mode"] == "workspace-write"
    assert checks[0] == {"type": "skill-used", "value": "bob"}
    assert checks[1]["type"] == "agent-rubric"
    assert checks[1]["threshold"] == 1.0
    assert "agents/example/SKILL.md" in checks[1]["value"]
    assert "Clear purpose" in checks[1]["value"]
    assert "via: disabled" in checks[1]["value"]
    assert "ignore capabilities from the host checkout" in checks[1]["value"]
    assert "do not require a Via Integration section" in checks[1]["value"]
    assert "packaged-copy instruction is not applicable" in checks[1]["value"]
    assert "The stated project-local state-file path is sufficient" in checks[1]["value"]
    assert checks[1]["provider"]["config"]["sandbox_mode"] == "read-only"


def test_build_config_does_not_apply_persona_context_to_decision_artifacts(
    tmp_path: Path,
) -> None:
    suite = {
        "id": "morpheus-design-advice",
        "persona": "morpheus",
        "request": "Use *advise to recommend a design.",
        "artifact": "docs/decisions/ADR-0001-example.md",
        "rubric": "agents/templates/_template_DECISION.md",
    }

    config = persona_eval.build_config(suite, tmp_path, "## Check — DECISION", "via: disabled")
    rubric_prompt = config["tests"][0]["assert"][1]["value"]

    assert "Use *advise" in config["prompts"][0]
    assert "DECISION" in rubric_prompt
    assert "packaged-copy instruction" not in rubric_prompt
    assert "canonical bob-protocol shared skill" not in rubric_prompt


def test_select_suites_by_persona_or_suite_id() -> None:
    suites = [
        {"id": "bob-persona-authoring", "persona": "bob"},
        {"id": "bob-protocol-smoke", "persona": "bob"},
        {"id": "neo-code-review", "persona": "neo"},
    ]

    assert [s["id"] for s in persona_eval.select_suites(suites, "bob")] == [
        "bob-persona-authoring",
        "bob-protocol-smoke",
    ]
    assert [s["id"] for s in persona_eval.select_suites(suites, "neo-code-review")] == [
        "neo-code-review"
    ]
