"""Run Promptfoo catalog evaluations against a fresh local BobProtocol install."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MODEL = "gpt-6-luna"
RUBRIC_START = "<!-- RUBRIC-START -->"
RUBRIC_END = "<!-- RUBRIC-END -->"


def find_project_root(start: Path | None = None) -> Path:
    """Find the Bob Protocol checkout containing the eval catalog."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "tools" / "persona-eval" / "catalog.json").is_file():
            return candidate
    raise FileNotFoundError("Could not find the Bob Protocol persona eval catalog.")


def load_catalog(path: Path) -> list[dict[str, Any]]:
    """Load and validate the versioned, manually curated evaluation catalog."""
    catalog = json.loads(path.read_text())
    if catalog.get("version") != 1 or not isinstance(catalog.get("suites"), list):
        raise ValueError("Eval catalog must use version 1 and contain a suites list.")
    suites = catalog["suites"]
    ids: set[str] = set()
    for suite in suites:
        required = ("id", "persona", "request", "artifact", "rubric")
        if any(not isinstance(suite.get(key), str) or not suite[key].strip() for key in required):
            raise ValueError("Each suite must define non-empty id, persona, request, artifact, and rubric fields.")
        if suite["id"] in ids:
            raise ValueError(f"Duplicate eval suite id: {suite['id']}")
        ids.add(suite["id"])
        if not isinstance(suite.get("tags", []), list):
            raise ValueError(f"Eval suite '{suite['id']}' tags must be a list.")
    return suites


def _project_path(project: Path, relative_path: str) -> Path:
    """Resolve a catalog path and reject paths that escape the temporary project."""
    resolved = (project / relative_path).resolve()
    if not resolved.is_relative_to(project.resolve()):
        raise ValueError(f"Eval catalog path escapes project: {relative_path}")
    return resolved


def extract_rubric(template: str) -> str:
    """Return the reviewer-only rubric embedded in an artifact template."""
    if RUBRIC_START not in template or RUBRIC_END not in template:
        raise ValueError("Artifact template does not contain RUBRIC-START/RUBRIC-END markers.")
    return template.split(RUBRIC_START, 1)[1].split(RUBRIC_END, 1)[0].strip()


def create_test_project(project: Path) -> None:
    """Create a tiny real project directory for bobp install."""
    project.mkdir(parents=True)
    (project / "README.md").write_text("# Persona eval fixture\n\nDisposable project for BobProtocol evaluation.\n")
    (project / "pyproject.toml").write_text(
        '[project]\nname = "bobp-persona-eval-fixture"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n'
    )


def install_local_bobp(root: Path, project: Path, temp_root: Path) -> None:
    """Run this checkout's bobp install while isolating global setup locations."""
    isolated_home = temp_root / "home"
    codex_home = temp_root / "codex-home"
    isolated_path = temp_root / "bin"
    isolated_tmp = temp_root / "tmp"
    isolated_home.mkdir(exist_ok=True)
    codex_home.mkdir(exist_ok=True)
    isolated_path.mkdir(exist_ok=True)
    isolated_tmp.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "HOME": str(isolated_home),
            "CODEX_HOME": str(codex_home),
            # Prevent optional via/Codex-global integrations during fixture setup.
            "PATH": str(isolated_path),
            "PYTHONPATH": str(root),
            "TMPDIR": str(isolated_tmp),
            "TMP": str(isolated_tmp),
            "TEMP": str(isolated_tmp),
        }
    )
    result = subprocess.run(
        [sys.executable, "-m", "bobp.cli", "install", str(project)],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Local bobp install failed in the disposable project.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def prepare_test_project(root: Path, project: Path, temp_root: Path) -> Path:
    """Create a project and populate it using bobp install from this checkout."""
    create_test_project(project)
    install_local_bobp(root, project, temp_root)
    expose_codex_skills(project)
    return project


def expose_codex_skills(project: Path) -> None:
    """Expose installed skills at Codex's project-local discovery path.

    bobp install also creates global CODEX_HOME links. The eval isolates that
    location, then links the installed skill files into the project's standard
    .agents/skills directory so the user's real Codex login remains in use.
    """
    dot_agents = project / ".agents"
    if dot_agents.is_symlink():
        dot_agents.unlink()
    elif dot_agents.exists():
        shutil.rmtree(dot_agents)
    skills_dir = dot_agents / "skills"
    skills_dir.mkdir(parents=True)

    agents_dir = project / "agents"
    sources = [
        child
        for child in agents_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    ]
    shared = agents_dir / "skills"
    if shared.is_dir():
        sources.extend(
            child
            for child in shared.iterdir()
            if child.is_dir() and (child / "SKILL.md").is_file()
        )
    for source in sources:
        link = skills_dir / source.name
        link.symlink_to(os.path.relpath(source, skills_dir), target_is_directory=True)
    if not (skills_dir / "bob" / "SKILL.md").is_file():
        raise RuntimeError("Installed Bob skill was not available at Codex's project-local path.")


def build_config(
    suite: dict[str, Any], project: Path, rubric_text: str, project_context: str
) -> dict[str, Any]:
    """Build an eval that checks actual installed skill use and artifact quality."""
    artifact = suite["artifact"]
    task = (
        f"{suite['request']}\n\n"
        "Create the requested artifact in the specified path. Do not commit changes "
        "or use network access. Choose routine conventions without asking the user."
    )
    judge_provider = {
        "id": "openai:codex-sdk",
        "config": {
            "model": MODEL,
            "working_dir": str(project),
            "skip_git_repo_check": True,
            "sandbox_mode": "read-only",
            "approval_policy": "never",
            "network_access_enabled": False,
            "web_search_mode": "disabled",
        },
    }
    rubric_context = ""
    if suite["rubric"].endswith("_template_PERSONA_SKILL.md"):
        rubric_context = (
            " This is a project-local persona skill in the installed target, not a persona "
            "packaged by BobProtocol, so the packaged-copy instruction is not applicable. "
            "A link to the canonical bob-protocol shared skill satisfies inherited "
            "state/chat/handoff rules; do not require redundant links to transitive dependencies. "
            "The stated project-local state-file path is sufficient for inherited state guidance; "
            "do not demand extra persona-specific checkpoint mechanics unless the linked "
            "shared protocol requires them."
        )
    return {
        "description": f"BobProtocol eval catalog: {suite['id']}",
        "tags": {"suite": suite["id"], "persona": suite["persona"]},
        "prompts": [task],
        "providers": [
            {
                "id": "openai:codex-sdk",
                "label": suite["persona"],
                "config": {
                    "model": MODEL,
                    "working_dir": str(project),
                    "skip_git_repo_check": True,
                    "sandbox_mode": "workspace-write",
                    "approval_policy": "never",
                    "network_access_enabled": False,
                    "web_search_mode": "disabled",
                    "enable_streaming": True,
                },
            }
        ],
        "tests": [
            {
                "description": f"{suite['id']} uses its installed skill and produces a rubric-compliant artifact",
                "assert": [
                    {"type": "skill-used", "value": suite["persona"]},
                    {
                        "type": "agent-rubric",
                        "value": (
                            f"Review the generated artifact at {artifact}. It must exist. "
                            "Judge it against every pass/fail criterion in the following "
                            "artifact rubric. Judge paths and commands against this "
                            "installed target project. The following is the authoritative "
                            "capability declaration from that fixture's agents/PROJECT.md; "
                            "ignore capabilities from the host checkout. In particular, do "
                            "not require a Via Integration section when via is disabled. "
                            f"{rubric_context}\n\n"
                            f"Fixture agents/PROJECT.md:\n```markdown\n{project_context}\n```\n\n"
                            "PASS only if all other applicable "
                            "criteria pass; otherwise fail.\n\n"
                            f"{rubric_text}"
                        ),
                        "threshold": 1.0,
                        "provider": judge_provider,
                    },
                ],
            }
        ],
    }


def run_suite(root: Path, suite: dict[str, Any], repeat: int = 1) -> int:
    """Run repeated, isolated copies of one catalog suite."""
    package_dir = root / "tools" / "persona-eval"
    promptfoo = package_dir / "node_modules" / ".bin" / "promptfoo"
    if not promptfoo.is_file():
        print("Promptfoo is not installed. Run `bobp make install-evals` first.", file=sys.stderr)
        return 2

    if repeat < 1:
        raise ValueError("repeat must be at least one")

    output_dir = root / "build" / "persona-eval"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runtime_dir = output_dir / "runtime"
    runtime_dir.mkdir(exist_ok=True)
    failures = 0
    for attempt in range(1, repeat + 1):
        run_dir = runtime_dir / f"{suite['id']}-{timestamp}-run{attempt}"
        run_dir.mkdir()
        project = run_dir / "project"
        prepare_test_project(root, project, run_dir)

        artifact_path = _project_path(project, suite["artifact"])
        rubric_path = _project_path(project, suite["rubric"])
        rubric_text = extract_rubric(rubric_path.read_text())
        project_context = (project / "agents" / "PROJECT.md").read_text()
        config = build_config(suite, project, rubric_text, project_context)
        config_path = run_dir / "promptfooconfig.json"
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        output_path = output_dir / f"{suite['id']}-{timestamp}-run{attempt}.json"
        isolated_tmp = run_dir / "tmp"
        isolated_tmp.mkdir(exist_ok=True)
        env = os.environ.copy()
        env.update({"TMPDIR": str(isolated_tmp), "TMP": str(isolated_tmp), "TEMP": str(isolated_tmp)})
        result = subprocess.run(
            [
                str(promptfoo),
                "eval",
                "--config",
                str(config_path),
                "--no-cache",
                "--output",
                str(output_path),
            ],
            cwd=root,
            env=env,
            check=False,
        )
        if not artifact_path.is_file():
            print(
                f"Eval did not create the expected artifact: {suite['artifact']}",
                file=sys.stderr,
            )
            failures += 1
        if result.returncode:
            failures += 1
        print(f"Eval project: {project}")
        print(f"Eval report: {output_path}")
    return 1 if failures else 0


def select_suites(suites: list[dict[str, Any]], selector: str) -> list[dict[str, Any]]:
    """Select suites by persona name or exact suite id."""
    return [suite for suite in suites if selector in (suite["id"], suite["persona"])]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run catalogued Promptfoo skill-use and artifact evaluations."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("selector", nargs="?", help="Persona name or eval suite id.")
    group.add_argument("--all", action="store_true", help="Run every suite in the catalog.")
    group.add_argument("--list", action="store_true", help="List catalog suites.")
    parser.add_argument("--repeat", type=int, default=1, help="Fresh runs per suite (default: 1).")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    try:
        root = find_project_root()
        suites = load_catalog(root / "tools" / "persona-eval" / "catalog.json")
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    if args.list:
        for suite in suites:
            print(f"{suite['id']}\t{suite['persona']}\t{', '.join(suite.get('tags', []))}")
        return

    if args.all:
        selected = suites
    else:
        selected = select_suites(suites, args.selector)
        if not selected:
            parser.error(f"No eval suites found for '{args.selector}'. Use --list to see the catalog.")

    failures = []
    for suite in selected:
        print(f"\n=== Eval suite: {suite['id']} ===", flush=True)
        code = run_suite(root, suite, args.repeat)
        if code:
            failures.append((suite["id"], code))
    if failures:
        for suite_id, code in failures:
            print(f"FAIL {suite_id} (Promptfoo exit {code})", file=sys.stderr)
        raise SystemExit(1)
    print("\nPASS: all selected eval suites passed.")


if __name__ == "__main__":
    main()
