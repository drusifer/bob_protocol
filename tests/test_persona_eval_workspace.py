"""Phase 3b of sprint 3: persona-eval results in the evaluating-skills workspace layout.

Layout and file shapes: https://agentskills.io/skill-creation/evaluating-skills
The Promptfoo result below has the shape of a real `promptfoo eval --output` report
(probed offline with the built-in `echo` provider on 2026-11-01).
"""

import json
from pathlib import Path
from typing import Any

import pytest

from bobp.tools import persona_eval_workspace as ws


def promptfoo_result(
    *, tokens: int = 1000, latency_ms: int = 2000, components: "list[dict[str, Any]] | None" = None,
    output: str = "final answer",
) -> dict[str, Any]:
    components = components if components is not None else [
        {"pass": True, "score": 1.0, "reason": "Installed persona skill: Codex read the skill."},
        {"pass": True, "score": 1.0, "reason": "Criterion one: meets (quote: 'evidence')."},
        {"pass": False, "score": 0.0, "reason": "Criterion two: does not meet."},
    ]
    return {
        "id": "r1",
        "success": all(c["pass"] for c in components),
        "score": 0.5,
        "latencyMs": latency_ms,
        "tokenUsage": {"prompt": 10, "completion": 20, "cached": 0, "total": tokens, "numRequests": 1},
        "response": {"output": output, "tokenUsage": {"total": tokens}},
        "gradingResult": {
            "pass": all(c["pass"] for c in components),
            "score": 0.5,
            "reason": "overall",
            "componentResults": components,
        },
    }


def promptfoo_report(result: dict[str, Any]) -> dict[str, Any]:
    return {"evalId": "eval-x", "results": {"version": 3, "results": [result], "stats": {}}}


class TestNaming:
    def test_workspace_is_beside_results_and_named_after_the_skill(self, tmp_path: Path) -> None:
        assert ws.workspace_dir(tmp_path, "neo") == tmp_path / "neo-workspace"

    @pytest.mark.parametrize("bad", ["", "../x", "a/b", "A", "a b", "-a", "x" * 65, ".."])
    def test_unsafe_skill_names_are_rejected(self, tmp_path: Path, bad: str) -> None:
        with pytest.raises(ValueError, match="skill name"):
            ws.workspace_dir(tmp_path, bad)

    def test_eval_directory_name(self) -> None:
        assert ws.eval_dir_name("morpheus-design-advice") == "eval-morpheus-design-advice"

    @pytest.mark.parametrize("bad", ["", "A-b", "a/b", "../a", "a b", "a.b"])
    def test_unsafe_suite_names_are_rejected(self, bad: str) -> None:
        with pytest.raises(ValueError, match="suite name"):
            ws.eval_dir_name(bad)


class TestIterations:
    def test_first_iteration_is_one(self, tmp_path: Path) -> None:
        assert ws.next_iteration(tmp_path / "missing") == 1
        (tmp_path / "w").mkdir()
        assert ws.next_iteration(tmp_path / "w") == 1

    def test_next_follows_the_highest_existing_and_ignores_noise(self, tmp_path: Path) -> None:
        for name in ("iteration-1", "iteration-3", "iteration-x", "notes", "iteration-02x"):
            (tmp_path / name).mkdir()
        (tmp_path / "iteration-9").write_text("a file, not an iteration")
        assert ws.next_iteration(tmp_path) == 4

    def test_make_iteration_creates_a_new_directory_and_never_reuses_one(self, tmp_path: Path) -> None:
        first = ws.make_iteration(tmp_path)
        second = ws.make_iteration(tmp_path)
        assert first.name == "iteration-1" and second.name == "iteration-2"
        assert first.is_dir() and second.is_dir()


class TestTimingAndGrading:
    def test_timing_uses_the_run_tokens_and_latency(self) -> None:
        assert ws.timing_from_result(promptfoo_result(tokens=84852, latency_ms=23332)) == {
            "total_tokens": 84852,
            "duration_ms": 23332,
        }

    def test_timing_defaults_to_zero_when_missing(self) -> None:
        assert ws.timing_from_result({}) == {"total_tokens": 0, "duration_ms": 0}

    def test_grading_has_one_entry_per_check_with_text_passed_and_evidence(self) -> None:
        grading = ws.grading_from_result(promptfoo_result(), ["The artifact meets the rubric"])

        assert [r["text"] for r in grading["assertion_results"]] == [
            "Installed persona skill",
            "Criterion one",
            "Criterion two",
        ]
        assert [r["passed"] for r in grading["assertion_results"]] == [True, True, False]
        assert "Codex read the skill" in grading["assertion_results"][0]["evidence"]
        assert grading["summary"] == {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.6667}
        assert grading["declared_assertions"] == ["The artifact meets the rubric"]

    def test_long_evidence_is_capped(self) -> None:
        components = [{"pass": True, "score": 1.0, "reason": "Check: " + "x" * 10000}]
        grading = ws.grading_from_result(promptfoo_result(components=components), [])
        assert len(grading["assertion_results"][0]["evidence"]) <= ws.MAX_EVIDENCE_CHARS

    def test_a_run_that_errored_before_grading_is_one_failed_entry(self) -> None:
        result = {"error": "provider crashed", "success": False, "latencyMs": 5}
        grading = ws.grading_from_result(result, [])
        assert grading["summary"] == {"passed": 0, "failed": 1, "total": 1, "pass_rate": 0.0}
        assert "provider crashed" in grading["assertion_results"][0]["evidence"]

    def test_reason_without_a_label_uses_the_assertion_type(self) -> None:
        components = [{"pass": True, "score": 1, "reason": "Assertion passed",
                       "assertion": {"type": "contains"}}]
        grading = ws.grading_from_result(promptfoo_result(components=components), [])
        assert grading["assertion_results"][0]["text"] == "contains"


class TestRunFiles:
    def test_write_run_creates_the_documented_files(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "iteration-1" / "eval-x" / "with_skill"
        artifact = tmp_path / "artifact.md"
        artifact.write_text("produced file\n")

        ws.write_run(run_dir, promptfoo_report(promptfoo_result()), ["declared"], artifact)

        assert json.loads((run_dir / "timing.json").read_text()) == {
            "total_tokens": 1000, "duration_ms": 2000
        }
        grading = json.loads((run_dir / "grading.json").read_text())
        assert grading["summary"]["total"] == 3 and grading["declared_assertions"] == ["declared"]
        assert (run_dir / "outputs" / "response.txt").read_text() == "final answer"
        assert (run_dir / "outputs" / "artifact.md").read_text() == "produced file\n"

    def test_write_run_without_an_artifact_still_writes_everything_else(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "w"
        ws.write_run(run_dir, promptfoo_report(promptfoo_result()), [], None)
        assert (run_dir / "grading.json").is_file()
        assert [p.name for p in (run_dir / "outputs").iterdir()] == ["response.txt"]

    def test_write_run_refuses_to_overwrite_an_earlier_run(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "w"
        ws.write_run(run_dir, promptfoo_report(promptfoo_result()), [], None)
        with pytest.raises(FileExistsError):
            ws.write_run(run_dir, promptfoo_report(promptfoo_result(tokens=1)), [], None)
        assert json.loads((run_dir / "timing.json").read_text())["total_tokens"] == 1000

    def test_a_report_without_results_is_an_error_not_a_crash(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="no results"):
            ws.write_run(tmp_path / "w", {"results": {"results": []}}, [], None)

    def test_artifact_symlink_is_not_followed(self, tmp_path: Path) -> None:
        secret = tmp_path / "secret.txt"
        secret.write_text("do not copy")
        link = tmp_path / "artifact.md"
        link.symlink_to(secret)
        run_dir = tmp_path / "w"
        ws.write_run(run_dir, promptfoo_report(promptfoo_result()), [], link)
        assert not (run_dir / "outputs" / "artifact.md").exists()


def _make_run(iteration: Path, eval_name: str, config: str, *, passed: int, total: int,
              tokens: int, ms: int) -> None:
    run = iteration / eval_name / config
    run.mkdir(parents=True)
    (run / "timing.json").write_text(json.dumps({"total_tokens": tokens, "duration_ms": ms}))
    (run / "grading.json").write_text(json.dumps({
        "assertion_results": [],
        "summary": {"passed": passed, "failed": total - passed, "total": total,
                    "pass_rate": round(passed / total, 4)},
    }))


class TestBenchmark:
    def test_summary_means_stddevs_and_delta(self, tmp_path: Path) -> None:
        it = tmp_path / "iteration-1"
        _make_run(it, "eval-a", "with_skill", passed=4, total=4, tokens=1000, ms=10000)
        _make_run(it, "eval-b", "with_skill", passed=2, total=4, tokens=3000, ms=30000)
        _make_run(it, "eval-a", "without_skill", passed=1, total=4, tokens=500, ms=5000)
        _make_run(it, "eval-b", "without_skill", passed=3, total=4, tokens=1500, ms=15000)

        benchmark = ws.write_benchmark(it)

        assert json.loads((it / "benchmark.json").read_text()) == benchmark
        with_skill = benchmark["run_summary"]["with_skill"]
        assert with_skill["pass_rate"] == {"mean": 0.75, "stddev": 0.25}
        assert with_skill["time_seconds"] == {"mean": 20.0, "stddev": 10.0}
        assert with_skill["tokens"] == {"mean": 2000.0, "stddev": 1000.0}
        baseline = benchmark["run_summary"]["without_skill"]
        assert baseline["pass_rate"] == {"mean": 0.5, "stddev": 0.25}
        assert baseline["tokens"] == {"mean": 1000.0, "stddev": 500.0}
        assert benchmark["run_summary"]["delta"] == {
            "pass_rate": 0.25, "time_seconds": 10.0, "tokens": 1000.0
        }

    def test_old_skill_baseline_is_reported_under_its_own_name(self, tmp_path: Path) -> None:
        it = tmp_path / "iteration-2"
        _make_run(it, "eval-a", "with_skill", passed=3, total=4, tokens=10, ms=1000)
        _make_run(it, "eval-a", "old_skill", passed=1, total=4, tokens=10, ms=1000)

        summary = ws.write_benchmark(it)["run_summary"]

        assert set(summary) == {"with_skill", "old_skill", "delta"}
        assert summary["delta"]["pass_rate"] == 0.5

    def test_without_a_baseline_there_is_no_delta(self, tmp_path: Path) -> None:
        it = tmp_path / "iteration-1"
        _make_run(it, "eval-a", "with_skill", passed=1, total=1, tokens=1, ms=1)
        assert "delta" not in ws.write_benchmark(it)["run_summary"]

    def test_repeated_runs_count_as_extra_samples(self, tmp_path: Path) -> None:
        it = tmp_path / "iteration-1"
        _make_run(it, "eval-a", "with_skill", passed=4, total=4, tokens=10, ms=1000)
        _make_run(it, "eval-a", "with_skill_run2", passed=2, total=4, tokens=10, ms=1000)
        summary = ws.write_benchmark(it)["run_summary"]["with_skill"]
        assert summary["pass_rate"] == {"mean": 0.75, "stddev": 0.25}

    def test_directories_without_results_are_ignored_and_an_empty_iteration_fails(
        self, tmp_path: Path
    ) -> None:
        it = tmp_path / "iteration-1"
        (it / "eval-a" / "with_skill").mkdir(parents=True)
        with pytest.raises(ValueError, match="no graded runs"):
            ws.write_benchmark(it)


class TestFeedbackAndSnapshot:
    def test_feedback_json_is_never_touched(self, tmp_path: Path) -> None:
        feedback = tmp_path / "feedback.json"
        feedback.write_text('{"eval-a": "axis labels missing"}')
        it = ws.make_iteration(tmp_path)
        _make_run(it, "eval-a", "with_skill", passed=1, total=1, tokens=1, ms=1)
        ws.write_benchmark(it)
        ws.make_iteration(tmp_path)
        assert feedback.read_text() == '{"eval-a": "axis labels missing"}'

    def test_snapshot_replaces_the_previous_copy(self, tmp_path: Path) -> None:
        skill = tmp_path / "skill"
        (skill / "evals").mkdir(parents=True)
        (skill / "SKILL.md").write_text("v2\n")
        workspace = tmp_path / "w"
        (workspace / "skill-snapshot").mkdir(parents=True)
        (workspace / "skill-snapshot" / "SKILL.md").write_text("v1\n")
        (workspace / "skill-snapshot" / "stale.txt").write_text("old")

        ws.snapshot_skill(skill, workspace)

        assert (workspace / "skill-snapshot" / "SKILL.md").read_text() == "v2\n"
        assert not (workspace / "skill-snapshot" / "stale.txt").exists()

    def test_snapshot_does_not_follow_symlinks_in_the_skill(self, tmp_path: Path) -> None:
        skill = tmp_path / "skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("v\n")
        secret = tmp_path / "secret.txt"
        secret.write_text("secret")
        (skill / "link.txt").symlink_to(secret)
        ws.snapshot_skill(skill, tmp_path / "w")
        copied = tmp_path / "w" / "skill-snapshot" / "link.txt"
        assert not copied.exists() or copied.is_symlink()

    def test_previous_snapshot_is_none_before_the_first_iteration(self, tmp_path: Path) -> None:
        assert ws.previous_snapshot(tmp_path) is None
        ws.snapshot_skill(_skill_dir(tmp_path), tmp_path / "w")
        assert ws.previous_snapshot(tmp_path / "w") == tmp_path / "w" / "skill-snapshot"


def _skill_dir(tmp_path: Path) -> Path:
    skill = tmp_path / "skill"
    skill.mkdir(exist_ok=True)
    (skill / "SKILL.md").write_text("v\n")
    return skill


class TestBaselineRequest:
    def test_sentences_that_name_the_skill_path_are_dropped(self) -> None:
        request = (
            "Use the Neo persona skill exposed at .agents/skills/neo/SKILL.md. "
            "Review this Python function. Keep it short."
        )
        assert ws.baseline_request(request) == "Review this Python function. Keep it short."

    def test_a_request_that_is_only_the_skill_sentence_is_kept_whole(self) -> None:
        request = "Use the skill at .agents/skills/x/SKILL.md."
        assert ws.baseline_request(request) == request

    def test_requests_without_a_skill_path_are_unchanged(self) -> None:
        assert ws.baseline_request("Do the thing.") == "Do the thing."
