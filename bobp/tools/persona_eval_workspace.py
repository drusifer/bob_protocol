"""Evaluation results in the Agent Skills "evaluating skills" workspace layout.

TLDR:
    https://agentskills.io/skill-creation/evaluating-skills keeps a skill's results
    beside it, not in it:

        <skill>-workspace/
            skill-snapshot/                 the skill version last evaluated (baseline source)
            feedback.json                   reviewer notes (never written by bobp)
            iteration-N/
                benchmark.json              mean/stddev per configuration, and the delta
                eval-<suite>/
                    with_skill/             outputs/, timing.json, grading.json
                    without_skill/          the same, run with the skill not exposed
                    old_skill/              the same, run with the previous skill version

    This module holds the pure, tested pieces: naming, iteration numbering, turning a
    Promptfoo result into timing.json and grading.json, benchmark.json, and the skill
    snapshot. persona_eval.py runs the evaluations and calls these to record them.
    Names that come from eval files are validated before they become path parts, and an
    earlier iteration or run is never overwritten.
"""

from __future__ import annotations

import json
import re
import shutil
import statistics
from pathlib import Path
from typing import Any

MAX_EVIDENCE_CHARS = 2000
BASELINES = ("without_skill", "old_skill")

_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ITERATION_RE = re.compile(r"^iteration-([1-9][0-9]*)$")
_CONFIG_RE = re.compile(r"^(with_skill|without_skill|old_skill)(?:_run\d+)?$")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _valid(name: str) -> bool:
    return isinstance(name, str) and 0 < len(name) <= 64 and _NAME_RE.match(name) is not None


def workspace_dir(output_dir: Path, skill: str) -> Path:
    """<output_dir>/<skill>-workspace, for a validated skill name."""
    if not _valid(skill):
        raise ValueError(f"Unsafe skill name for an evaluation workspace: {skill!r}")
    return output_dir / f"{skill}-workspace"


def eval_dir_name(suite: str) -> str:
    """eval-<suite> for a validated suite name."""
    if not _valid(suite):
        raise ValueError(f"Unsafe suite name for an evaluation folder: {suite!r}")
    return f"eval-{suite}"


def next_iteration(workspace: Path) -> int:
    """One more than the highest existing iteration-N directory (1 for a new workspace)."""
    if not workspace.is_dir():
        return 1
    highest = 0
    for child in workspace.iterdir():
        match = _ITERATION_RE.match(child.name)
        if match and child.is_dir() and not child.is_symlink():
            highest = max(highest, int(match.group(1)))
    return highest + 1


def make_iteration(workspace: Path) -> Path:
    """Create the next iteration directory; an existing one is never reused."""
    workspace.mkdir(parents=True, exist_ok=True)
    directory = workspace / f"iteration-{next_iteration(workspace)}"
    directory.mkdir()
    return directory


def timing_from_result(result: dict[str, Any]) -> dict[str, int]:
    """timing.json content: total tokens and duration of one Promptfoo result."""
    usage = result.get("tokenUsage") or {}
    tokens = usage.get("total") if isinstance(usage, dict) else 0
    latency = result.get("latencyMs")
    return {
        "total_tokens": int(tokens) if isinstance(tokens, (int, float)) else 0,
        "duration_ms": int(latency) if isinstance(latency, (int, float)) else 0,
    }


def _cap(text: Any) -> str:
    return str(text)[:MAX_EVIDENCE_CHARS]


def _label(component: dict[str, Any], position: int) -> str:
    reason = component.get("reason")
    if isinstance(reason, str) and ": " in reason:
        return reason.split(": ", 1)[0][:200]
    assertion = component.get("assertion")
    if isinstance(assertion, dict) and isinstance(assertion.get("type"), str):
        return assertion["type"]
    return f"check {position}"


def grading_from_result(result: dict[str, Any], declared_assertions: list[str]) -> dict[str, Any]:
    """grading.json content: one entry per graded check, plus a summary.

    The checks are what the evaluator actually grades (the skill-use check and each
    rubric or behavior criterion), each with the grader's reason as evidence. The
    eval's declared assertions are carried along as the stated intent.
    """
    grading = result.get("gradingResult") if isinstance(result.get("gradingResult"), dict) else {}
    components = grading.get("componentResults") if isinstance(grading, dict) else None
    entries: list[dict[str, Any]] = []
    if isinstance(components, list) and components:
        for position, component in enumerate(components, start=1):
            if not isinstance(component, dict):
                continue
            entries.append(
                {
                    "text": _label(component, position),
                    "passed": bool(component.get("pass")),
                    "evidence": _cap(component.get("reason", "")),
                }
            )
    elif result.get("error"):
        entries.append({"text": "run completed", "passed": False, "evidence": _cap(result["error"])})
    elif grading:
        entries.append(
            {"text": "overall", "passed": bool(grading.get("pass")), "evidence": _cap(grading.get("reason", ""))}
        )
    else:
        entries.append({"text": "run graded", "passed": False, "evidence": "No grading result was produced."})
    passed = sum(1 for entry in entries if entry["passed"])
    total = len(entries)
    return {
        "assertion_results": entries,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "declared_assertions": list(declared_assertions),
    }


def write_run(
    run_dir: Path,
    report: dict[str, Any],
    declared_assertions: list[str],
    artifact: Path | None,
) -> None:
    """Record one run (with_skill, without_skill or old_skill) from a Promptfoo report.

    Raises FileExistsError if the run directory already exists, so earlier results are
    never overwritten, and ValueError if the report holds no result.
    """
    results = (report.get("results") or {}).get("results") if isinstance(report, dict) else None
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise ValueError("The Promptfoo report has no results to record.")
    result = results[0]
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)

    response = result.get("response") if isinstance(result.get("response"), dict) else {}
    output = response.get("output", "")
    (outputs / "response.txt").write_text(
        output if isinstance(output, str) else json.dumps(output, indent=2), encoding="utf-8"
    )
    if artifact is not None and artifact.is_file() and not artifact.is_symlink():
        shutil.copyfile(artifact, outputs / artifact.name)

    (run_dir / "timing.json").write_text(
        json.dumps(timing_from_result(result), indent=2) + "\n", encoding="utf-8"
    )
    (run_dir / "grading.json").write_text(
        json.dumps(grading_from_result(result, declared_assertions), indent=2) + "\n",
        encoding="utf-8",
    )


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(statistics.fmean(values), 4),
        "stddev": round(statistics.pstdev(values), 4) if len(values) > 1 else 0.0,
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_benchmark(iteration_dir: Path) -> dict[str, Any]:
    """Aggregate every graded run in an iteration into benchmark.json and return it."""
    samples: dict[str, dict[str, list[float]]] = {}
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        for run in sorted(eval_dir.iterdir()) if eval_dir.is_dir() else []:
            match = _CONFIG_RE.match(run.name)
            grading_path, timing_path = run / "grading.json", run / "timing.json"
            if not (match and run.is_dir() and grading_path.is_file() and timing_path.is_file()):
                continue
            grading, timing = _load_json(grading_path), _load_json(timing_path)
            bucket = samples.setdefault(
                match.group(1), {"pass_rate": [], "time_seconds": [], "tokens": []}
            )
            bucket["pass_rate"].append(float(grading["summary"]["pass_rate"]))
            bucket["time_seconds"].append(float(timing["duration_ms"]) / 1000.0)
            bucket["tokens"].append(float(timing["total_tokens"]))
    if "with_skill" not in samples:
        raise ValueError(f"{iteration_dir}: no graded runs to summarize.")

    summary: dict[str, Any] = {
        config: {metric: _stats(values) for metric, values in metrics.items()}
        for config, metrics in samples.items()
    }
    baseline = next((name for name in BASELINES if name in summary), None)
    if baseline is not None:
        summary["delta"] = {
            metric: round(summary["with_skill"][metric]["mean"] - summary[baseline][metric]["mean"], 4)
            for metric in ("pass_rate", "time_seconds", "tokens")
        }
    benchmark = {"run_summary": summary}
    (iteration_dir / "benchmark.json").write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    return benchmark


def snapshot_skill(skill_dir: Path, workspace: Path) -> Path:
    """Replace <workspace>/skill-snapshot with a copy of the skill (links copied as links)."""
    if skill_dir.is_symlink() or not skill_dir.is_dir():
        raise ValueError(f"Cannot snapshot {skill_dir}: not a skill directory.")
    workspace.mkdir(parents=True, exist_ok=True)
    target = workspace / "skill-snapshot"
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill_dir, target, symlinks=True)
    return target


def previous_snapshot(workspace: Path) -> Path | None:
    """The snapshot of the skill version last evaluated, if there is one."""
    target = workspace / "skill-snapshot"
    return target if target.is_dir() and not target.is_symlink() else None


def baseline_request(request: str) -> str:
    """The same request without the sentence(s) that point at the skill under test."""
    sentences = _SENTENCE_RE.split(request.strip())
    kept = [sentence for sentence in sentences if ".agents/skills/" not in sentence]
    return " ".join(kept) if kept else request
