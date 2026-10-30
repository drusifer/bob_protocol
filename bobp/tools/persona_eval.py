"""Run Promptfoo catalog evaluations against a fresh local BobProtocol install."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

ASSET_PACKAGE = "bobp.tools.persona_eval_assets"
MODEL = "gpt-6-luna"
RUBRIC_START = "<!-- RUBRIC-START -->"
RUBRIC_END = "<!-- RUBRIC-END -->"


def find_project_root(start: Path | None = None) -> Path:
    """Find the nearest project root, without assuming a Makefile or Bobp checkout."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if any(
            (candidate / marker).exists()
            for marker in (".git", "pyproject.toml", "package.json", "AGENTS.md", "README.md")
        ):
            return candidate
    return current


def load_catalog(path: Path | None = None) -> list[dict[str, Any]]:
    """Load and validate the package's versioned evaluation catalog or a test file."""
    if path is None:
        catalog_text = files(ASSET_PACKAGE).joinpath("catalog.json").read_text(encoding="utf-8")
    else:
        catalog_text = path.read_text(encoding="utf-8")
    catalog = json.loads(catalog_text)
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


def install_local_bobp(project: Path, temp_root: Path) -> None:
    """Run the active Bobp installation while isolating global setup locations."""
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
            "TMPDIR": str(isolated_tmp),
            "TMP": str(isolated_tmp),
            "TEMP": str(isolated_tmp),
        }
    )
    result = subprocess.run(
        [sys.executable, "-m", "bobp.cli", "install", str(project)],
        cwd=project,
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


def prepare_test_project(project: Path, temp_root: Path) -> Path:
    """Create a project and populate it using the active Bobp installation."""
    create_test_project(project)
    install_local_bobp(project, temp_root)
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


def _npm_command(*args: str) -> list[str] | None:
    """Return an npm argv that also works when Windows resolves npm.cmd."""
    npm = shutil.which("npm")
    if not npm:
        return None
    if os.name == "nt" and Path(npm).suffix.lower() in {".cmd", ".bat"}:
        return ["cmd", "/c", npm, *args]
    return [npm, *args]


def check_node_prerequisites() -> str | None:
    """Return a user-facing error when the required Node.js/npm runtime is unavailable."""
    node = shutil.which("node")
    if not node:
        return "persona-eval requires Node.js >=22.22.0 and npm. Install Node.js from https://nodejs.org/ and retry."

    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True, check=False)
    except OSError as exc:
        return f"Could not run Node.js at {node}: {exc}. Install Node.js >=22.22.0 and retry."
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?", result.stdout.strip())
    if result.returncode or not match:
        detail = result.stderr.strip() or result.stdout.strip() or "no version was reported"
        return f"Could not determine the Node.js version ({detail}). Install Node.js >=22.22.0 and retry."
    version = tuple(int(part) for part in match.groups())
    if version < (22, 22, 0):
        reported = result.stdout.strip()
        return f"persona-eval requires Node.js >=22.22.0; found {reported}. Upgrade Node.js and retry."
    if not shutil.which("npm"):
        return "persona-eval requires npm, but npm was not found on PATH. Install npm with Node.js >=22.22.0 and retry."
    return None


def _npm_eval_dependencies() -> dict[str, str]:
    """Read pinned npm requirements from the package's dependency manifest."""
    manifest = json.loads(files(ASSET_PACKAGE).joinpath("package.json").read_text(encoding="utf-8"))
    return manifest["devDependencies"]


def _npm_install_hint() -> str:
    packages = " ".join(f"{name}@{version}" for name, version in _npm_eval_dependencies().items())
    return f"npm install --global {packages}"


def show_node_setup_instructions() -> int:
    """Print global npm setup instructions without writing to the target project."""
    prerequisite_error = check_node_prerequisites()
    if prerequisite_error:
        print(prerequisite_error, file=sys.stderr)
        return 2

    print("Install the persona-evaluation npm dependencies globally with:")
    print(f"  {_npm_install_hint()}")
    print("Then rerun the evaluation command. Bobp did not install anything.")
    return 0


def _global_node_runtime_error() -> str | None:
    """Check that the pinned Promptfoo and Codex SDK packages are installed globally."""
    npm = _npm_command("root", "--global")
    if npm is None:
        return "npm was not found on PATH. Install npm with Node.js >=22.22.0 and retry."
    result = subprocess.run(npm, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "npm root --global failed"
        return f"Could not locate globally installed npm packages ({detail}). Run `bobp persona-eval --setup` for instructions."

    modules = Path(result.stdout.strip())
    dependencies = _npm_eval_dependencies()
    missing = []
    for name, expected in dependencies.items():
        manifest = modules / name / "package.json"
        try:
            installed = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            missing.append(f"{name}@{expected}")
            continue
        if installed.get("version") != expected:
            missing.append(f"{name}@{expected}")
    if missing:
        return (
            "Required global npm dependencies are missing or have the wrong version: "
            f"{', '.join(missing)}. Run `{_npm_install_hint()}` and retry."
        )
    if shutil.which("promptfoo") is None:
        return "The global Promptfoo command is not on PATH. Add npm's global executable directory to PATH and retry."
    return None


def build_config(
    suite: dict[str, Any], project: Path, rubric_text: str, project_context: str
) -> dict[str, Any]:
    """Build an eval that checks actual installed skill use and artifact quality."""
    artifact = suite["artifact"]
    if suite.get("evaluation_scope") == "personality-behavior":
        task = (
            f"{suite['request']}\n\n"
            "This is a response-only evaluation. Answer the scenario in your final response; do not "
            "create a deliverable or change your installed skill. Follow required state/chat protocol "
            "only if it applies. Do not commit changes or use network access. Choose routine conventions "
            "without asking the user."
        )
    else:
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
    if suite.get("evaluation_scope") == "personality-behavior":
        target_skill_text = (project / artifact).read_text(encoding="utf-8")
        rubric_text = (
            "Evaluate only this persona-upgrade scope. Inspect the existing target persona skill at "
            f"{artifact}: its Personality Traits & Values section must explicitly state the shared "
            "baseline traits courteous, succinct, and respectful; include a role-fitting demeanor; "
            "and list 3–5 useful, role-specific working values. Then evaluate the provider's final "
            "response to the scenario against the persona's role and the additional behavior criteria "
            f"below. The full target skill content is included as evidence; do not rely on a workspace "
            f"read. Do not score unrelated legacy instructions, responsibilities, or command-interface "
            f"criteria.\n\nTarget skill content for {artifact}:\n```markdown\n{target_skill_text}\n```"
            f"\n\nAdditional behavior criteria:\n{suite['behavior_criteria']}"
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
                "description": (
                    f"{suite['id']} uses its installed skill and demonstrates the required behavior"
                    if suite.get("evaluation_scope") == "personality-behavior"
                    else f"{suite['id']} uses its installed skill and produces a rubric-compliant artifact"
                ),
                "assert": [
                    {"type": "skill-used", "value": suite["persona"]},
                    {
                        "type": "agent-rubric",
                        "value": (
                            (
                                f"The target skill at {artifact} already exists; inspect its personality section "
                                "and assess the provider's final response to the scenario. "
                                if suite.get("evaluation_scope") == "personality-behavior"
                                else f"Review the generated artifact at {artifact}. It must exist. "
                            )
                            + "Judge the applicable pass/fail criteria in the following "
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
    prerequisite_error = check_node_prerequisites()
    if prerequisite_error:
        print(prerequisite_error, file=sys.stderr)
        return 2

    runtime_error = _global_node_runtime_error()
    if runtime_error:
        print(runtime_error, file=sys.stderr)
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
        prepare_test_project(project, run_dir)

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
        promptfoo = shutil.which("promptfoo")
        if not promptfoo:
            print("The global Promptfoo command is not on PATH. Add npm's global executable directory to PATH and retry.", file=sys.stderr)
            return 2
        command = [
            promptfoo,
            "eval",
            "--config",
            str(config_path),
            "--no-cache",
            "--output",
            str(output_path),
        ]
        if os.name == "nt" and Path(promptfoo).suffix.lower() in {".cmd", ".bat"}:
            command = ["cmd", "/c", *command]
        result = subprocess.run(
            command,
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
    group.add_argument("--setup", action="store_true", help="Show instructions for installing locked npm dependencies globally.")
    parser.add_argument("--repeat", type=int, default=1, help="Fresh runs per suite (default: 1).")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    try:
        root = find_project_root()
        suites = load_catalog()
    except ValueError as exc:
        parser.error(str(exc))

    if args.setup:
        raise SystemExit(show_node_setup_instructions())

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
