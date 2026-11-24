"""Phase 3b of sprint 3: the runner records with-skill and baseline runs in the workspace.

Promptfoo is replaced by a fake that writes a report with the real shape, so nothing
here calls Codex, Jev or any external service.
"""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

from bobp.tools import _bob_manage, persona_eval
from bobp.tools import persona_eval_workspace as ws


def _suite(**overrides: Any) -> dict[str, Any]:
    suite = {
        "id": "neo-personality",
        "persona": "neo",
        "skill": "neo",
        "eval_id": 1,
        "request": (
            "Use the Neo persona skill exposed at .agents/skills/neo/SKILL.md. Review this function."
        ),
        "expected_output": "A review.",
        "assertions": ["Reviews the function"],
        "artifact": ".agents/skills/neo/SKILL.md",
        "rubric": "agents/templates/_template_PERSONA_SKILL.md",
        "tags": [],
        "evaluation_scope": "personality-behavior",
        "behavior_criteria": "Names a concrete defect",
    }
    suite.update(overrides)
    return suite


def _report(passed: bool = True) -> dict[str, Any]:
    components = [
        {"pass": True, "score": 1.0, "reason": "Installed persona skill: read."},
        {"pass": passed, "score": 1.0 if passed else 0.0, "reason": "Behavior 1: judged."},
    ]
    return {
        "results": {
            "results": [
                {
                    "latencyMs": 1500,
                    "tokenUsage": {"total": 400},
                    "response": {"output": "the answer"},
                    "gradingResult": {"pass": passed, "componentResults": components},
                }
            ]
        }
    }


class FakePromptfoo:
    """Stands in for `promptfoo eval`; records each config and writes a report."""

    def __init__(self, fail_baseline: bool = False) -> None:
        self.configs: list[dict[str, Any]] = []
        self.fail_baseline = fail_baseline

    def __call__(self, command: list[str], **_kwargs: Any) -> Any:
        if "--config" not in command:  # e.g. the fixture's `git` probe
            return SimpleNamespace(returncode=1, stdout="", stderr="")
        config = json.loads(Path(command[command.index("--config") + 1]).read_text())
        self.configs.append(config)
        baseline = len(config["tests"][0]["assert"]) == 1
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_report(passed=not (baseline and self.fail_baseline))))
        return SimpleNamespace(returncode=1 if baseline and self.fail_baseline else 0)


@pytest.fixture()
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    root = tmp_path / "root"
    root.mkdir()
    fake = FakePromptfoo()
    monkeypatch.setattr(persona_eval, "check_jev_prerequisites", lambda: None)
    monkeypatch.setattr(persona_eval, "check_node_prerequisites", lambda: None)
    monkeypatch.setattr(persona_eval, "_global_node_runtime_error", lambda: None)
    monkeypatch.setattr(persona_eval.shutil, "which", lambda _name: "/usr/bin/promptfoo")
    monkeypatch.setattr(persona_eval.subprocess, "run", fake)

    def install(project: Path, _temp_root: Path) -> None:
        with patch.object(_bob_manage, "_run_setup_agent_links"):
            _bob_manage.install(project)
        (project / "agents" / "PROJECT.md").write_text("via: disabled\n")

    monkeypatch.setattr(persona_eval, "install_local_bobp", install)
    return SimpleNamespace(root=root, fake=fake, iteration=tmp_path / "ws" / "iteration-1")


def _run(runner: SimpleNamespace, **kwargs: Any) -> int:
    runner.iteration.mkdir(parents=True, exist_ok=True)
    return persona_eval.run_suite(
        runner.root, _suite(), kwargs.pop("repeat", 1), iteration_dir=runner.iteration, **kwargs
    )


def test_with_skill_run_is_recorded_in_the_documented_layout(runner: SimpleNamespace) -> None:
    assert _run(runner) == 0

    run = runner.iteration / "eval-neo-personality" / "with_skill"
    assert json.loads((run / "timing.json").read_text()) == {"total_tokens": 400, "duration_ms": 1500}
    grading = json.loads((run / "grading.json").read_text())
    assert grading["summary"]["total"] == 2
    assert grading["declared_assertions"] == ["Reviews the function"]
    assert (run / "outputs" / "response.txt").read_text() == "the answer"
    assert not (runner.iteration / "eval-neo-personality" / "without_skill").exists()
    assert len(runner.fake.configs) == 1


def test_without_skill_baseline_runs_the_same_request_without_the_skill(
    runner: SimpleNamespace,
) -> None:
    assert _run(runner, baseline="without-skill") == 0

    with_cfg, baseline_cfg = runner.fake.configs
    assert ".agents/skills/" in with_cfg["prompts"][0]
    assert ".agents/skills/" not in baseline_cfg["prompts"][0]
    assert "Review this function." in baseline_cfg["prompts"][0]
    assert len(baseline_cfg["tests"][0]["assert"]) == 1
    base_run = runner.iteration / "eval-neo-personality" / "without_skill"
    assert (base_run / "grading.json").is_file() and (base_run / "timing.json").is_file()
    baseline_project = Path(baseline_cfg["providers"][0]["config"]["working_dir"])
    assert not (baseline_project / ".agents" / "skills" / "neo").exists()
    assert not (baseline_project / ".agents" / "skills" / "neo").exists()
    assert (baseline_project / ".agents" / "skills" / "mouse").exists()  # other skills stay


def test_previous_baseline_runs_the_snapshotted_skill_as_old_skill(
    runner: SimpleNamespace, tmp_path: Path
) -> None:
    snapshot = tmp_path / "snap"
    snapshot.mkdir()
    (snapshot / "SKILL.md").write_text("OLD VERSION of the skill\n")

    assert _run(runner, baseline="previous", snapshot=snapshot) == 0

    baseline_cfg = runner.fake.configs[1]
    baseline_project = Path(baseline_cfg["providers"][0]["config"]["working_dir"])
    installed = baseline_project / ".agents" / "skills" / "neo" / "SKILL.md"
    assert installed.read_text() == "OLD VERSION of the skill\n"
    assert (runner.iteration / "eval-neo-personality" / "old_skill" / "grading.json").is_file()
    assert not (runner.iteration / "eval-neo-personality" / "without_skill").exists()


def test_previous_baseline_without_a_snapshot_falls_back_to_without_skill(
    runner: SimpleNamespace, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(runner, baseline="previous", snapshot=None) == 0

    assert (runner.iteration / "eval-neo-personality" / "without_skill").is_dir()
    assert "no earlier version" in capsys.readouterr().out.lower()


def test_repeat_records_each_attempt_under_its_own_name(runner: SimpleNamespace) -> None:
    assert _run(runner, repeat=2, baseline="without-skill") == 0

    case = runner.iteration / "eval-neo-personality"
    assert sorted(p.name for p in case.iterdir()) == [
        "with_skill", "with_skill_run2", "without_skill", "without_skill_run2",
    ]


def test_a_failing_baseline_does_not_fail_the_suite(
    runner: SimpleNamespace,
) -> None:
    runner.fake.fail_baseline = True
    assert _run(runner, baseline="without-skill") == 0
    grading = json.loads(
        (runner.iteration / "eval-neo-personality" / "without_skill" / "grading.json").read_text()
    )
    assert grading["summary"]["failed"] == 1


def test_an_earlier_run_is_never_overwritten(runner: SimpleNamespace) -> None:
    _run(runner)
    first = (runner.iteration / "eval-neo-personality" / "with_skill" / "timing.json").read_text()
    runner.fake.configs.clear()

    _run(runner)  # same iteration directory again: the recorded run must survive

    assert (runner.iteration / "eval-neo-personality" / "with_skill" / "timing.json").read_text() == first


def test_without_an_iteration_directory_nothing_is_recorded(runner: SimpleNamespace) -> None:
    assert persona_eval.run_suite(runner.root, _suite(), 1) == 0
    assert not runner.iteration.exists()


def test_unsafe_suite_names_cannot_choose_the_workspace_folder(runner: SimpleNamespace) -> None:
    bad = _suite(id="../../escape")
    runner.iteration.mkdir(parents=True)
    persona_eval.run_suite(runner.root, bad, 1, iteration_dir=runner.iteration)
    assert not (runner.iteration.parent.parent / "escape").exists()
    assert [p.name for p in runner.iteration.iterdir()] == []


def test_main_creates_a_new_iteration_each_time_and_writes_benchmark_and_snapshot(
    runner: SimpleNamespace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(persona_eval, "find_project_root", lambda: runner.root)

    persona_eval.main(["neo-personality", "--baseline", "without-skill"])
    persona_eval.main(["neo-personality", "--baseline", "previous"])

    workspace_dir = runner.root / "build" / "persona-eval" / "neo-workspace"
    first, second = workspace_dir / "iteration-1", workspace_dir / "iteration-2"
    assert (first / "benchmark.json").is_file() and (second / "benchmark.json").is_file()
    assert "without_skill" in json.loads((first / "benchmark.json").read_text())["run_summary"]
    assert "old_skill" in json.loads((second / "benchmark.json").read_text())["run_summary"]
    assert (workspace_dir / "skill-snapshot" / "SKILL.md").is_file()
    out = capsys.readouterr().out
    assert "iteration-1" in out and "iteration-2" in out
    assert "baseline" in out.lower()


def test_a_run_that_produced_nothing_leaves_no_empty_iteration(
    runner: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(persona_eval, "find_project_root", lambda: runner.root)
    monkeypatch.setattr(persona_eval, "check_node_prerequisites", lambda: "Node.js is missing.")

    with pytest.raises(SystemExit):
        persona_eval.main(["neo-personality"])

    workspace_dir = runner.root / "build" / "persona-eval" / "neo-workspace"
    assert not list(workspace_dir.glob("iteration-*"))
    assert ws.next_iteration(workspace_dir) == 1


def test_main_leaves_feedback_json_alone(
    runner: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(persona_eval, "find_project_root", lambda: runner.root)
    workspace_dir = runner.root / "build" / "persona-eval" / "neo-workspace"
    workspace_dir.mkdir(parents=True)
    (workspace_dir / "feedback.json").write_text('{"eval-neo-personality": "too terse"}')

    persona_eval.main(["neo-personality"])

    assert (workspace_dir / "feedback.json").read_text() == '{"eval-neo-personality": "too terse"}'


def test_workspace_helper_names_match_the_documented_layout() -> None:
    assert ws.eval_dir_name("neo-personality") == "eval-neo-personality"
