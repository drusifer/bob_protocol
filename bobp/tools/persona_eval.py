"""Run Promptfoo evaluations from each skill's evals/evals.json against a fresh local install."""

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
from pathlib import Path, PurePosixPath
from typing import Any

from . import persona_eval_workspace as workspace
from .persona_eval_workspace import baseline_request

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


MAX_EVALS_BYTES = 1024 * 1024
PACKAGED_AGENTS = Path(__file__).resolve().parent.parent / "templates" / "agents"


def _escapes(relative_path: str) -> bool:
    """True if a path from an eval file is absolute or climbs out with '..'."""
    path = PurePosixPath(relative_path.replace("\\", "/"))
    return path.is_absolute() or ".." in path.parts or bool(re.match(r"^[A-Za-z]:", relative_path))


def _read_evals_file(path: Path) -> Any:
    """Parse one evals.json, refusing symlinks and oversized files, naming the file in errors."""
    if path.is_symlink():
        raise ValueError(f"{path}: evals.json must not be a symlink.")
    if path.stat().st_size > MAX_EVALS_BYTES:
        raise ValueError(f"{path}: evals.json is too large (limit {MAX_EVALS_BYTES} bytes).")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path}: not valid JSON ({exc}).") from exc


def _text(entry: dict[str, Any], key: str, where: str, label: str | None = None) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: '{label or key}' must be a non-empty string.")
    return value


def _validate_eval(entry: Any, path: Path, skill: str, position: int) -> dict[str, Any]:
    """Validate one eval from <skill>/evals/evals.json and return it as an evaluator suite."""
    where = f"{path} (evals[{position}])"
    if not isinstance(entry, dict):
        raise ValueError(f"{where}: each eval must be an object.")
    eval_id = entry.get("id")
    if isinstance(eval_id, bool) or not isinstance(eval_id, int):
        raise ValueError(f"{where}: 'id' must be an integer.")
    prompt = _text(entry, "prompt", where)
    expected = _text(entry, "expected_output", where)
    assertions = entry.get("assertions")
    if (
        not isinstance(assertions, list)
        or not assertions
        or any(not isinstance(item, str) or not item.strip() for item in assertions)
    ):
        raise ValueError(f"{where}: 'assertions' must be a non-empty list of non-empty strings.")
    files_field = entry.get("files", [])
    if not isinstance(files_field, list) or any(not isinstance(item, str) for item in files_field):
        raise ValueError(f"{where}: 'files' must be a list of strings.")
    for item in files_field:
        if _escapes(item):
            raise ValueError(f"{where}: file path escapes the skill directory: {item}")
    extras = entry.get("bobp")
    if not isinstance(extras, dict):
        raise ValueError(f"{where}: 'bobp' must be an object with the evaluator settings.")
    suite = {
        "id": _text(extras, "suite", where, "bobp.suite"),
        "persona": _text(extras, "persona", where, "bobp.persona"),
        "skill": skill,
        "eval_id": eval_id,
        "request": prompt,
        "expected_output": expected,
        "assertions": assertions,
        "artifact": _text(extras, "artifact", where, "bobp.artifact"),
        "rubric": _text(extras, "rubric", where, "bobp.rubric"),
    }
    for key in ("artifact", "rubric"):
        if _escapes(suite[key]):
            raise ValueError(f"{where}: bobp.{key} path escapes the project: {suite[key]}")
    tags = extras.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError(f"{where}: 'bobp.tags' must be a list of strings.")
    suite["tags"] = tags
    for key in ("evaluation_scope", "behavior_criteria"):
        if key in extras:
            suite[key] = _text(extras, key, where, f"bobp.{key}")
    if files_field:
        suite["files"] = files_field
    return suite


def load_evals(root: Path | None = None) -> list[dict[str, Any]]:
    """Load every skill's evals/evals.json under `root` (default: the packaged templates).

    Looks in <root>/<persona>/evals/evals.json and <root>/skills/<skill>/evals/evals.json.
    Each file follows https://agentskills.io/skill-creation/evaluating-skills (`skill_name`
    and `evals`, each eval with `id`, `prompt`, `expected_output`, `assertions`, optional
    `files`); the evaluator's own settings live in the eval's `bobp` object. Raises
    ValueError naming the file and field for anything malformed.
    """
    root = PACKAGED_AGENTS if root is None else root
    paths = sorted(root.glob("*/evals/evals.json")) + sorted(root.glob("skills/*/evals/evals.json"))
    suites: list[dict[str, Any]] = []
    suite_ids: set[str] = set()
    for path in paths:
        document = _read_evals_file(path)
        if not isinstance(document, dict):
            raise ValueError(f"{path}: must contain a JSON object.")
        skill = path.parent.parent.name
        if document.get("skill_name") != skill:
            raise ValueError(f"{path}: 'skill_name' must be '{skill}'.")
        evals = document.get("evals")
        if not isinstance(evals, list) or not evals:
            raise ValueError(f"{path}: 'evals' must be a non-empty list.")
        ids: set[int] = set()
        for position, entry in enumerate(evals):
            suite = _validate_eval(entry, path, skill, position)
            if suite["eval_id"] in ids:
                raise ValueError(f"{path}: Duplicate eval id {suite['eval_id']}.")
            ids.add(suite["eval_id"])
            if suite["id"] in suite_ids:
                raise ValueError(f"Duplicate eval suite id: {suite['id']}")
            suite_ids.add(suite["id"])
            suites.append(suite)
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


def extract_rubric_criteria(
    rubric_text: str, scenario: str = ""
) -> list[dict[str, Any]]:
    """Turn rubric checklist rows into individually judgeable criteria."""
    criteria: list[dict[str, Any]] = []
    for line in rubric_text.splitlines():
        match = re.match(r"^\s*-\s+\[ \]\s+(.*\S)\s*$", line)
        if not match:
            continue
        text = match.group(1)
        # The DECISION rubric's FAIL row is an aggregate gate, not a separate criterion.
        if text.startswith("**FAIL**"):
            continue
        label_match = re.match(r"\*\*(?P<label>[^*]+?):\*\*\s*.+", text)
        if not label_match:
            label_match = re.match(r"\*\*(?P<label>[^*]+)\*\*\s*—\s*.+", text)
        label = label_match.group("label") if label_match else f"criterion-{len(criteria) + 1}"
        criterion: dict[str, Any] = {
            "id": f"criterion_{len(criteria) + 1}",
            "label": label,
            "text": text,
            "applicable": True,
        }
        if "For any eval scenario that specifies an L1" in text and not re.search(
            r"\bL[1-4]\b", scenario
        ):
            criterion["applicable"] = False
            criterion["not_applicable_reason"] = "Scenario does not specify an L1–L4 task level."
        criteria.append(criterion)
    if not criteria:
        raise ValueError("Eval rubric must contain at least one unchecked criterion row.")
    return criteria


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


def expose_codex_skills(project: Path, required: str | None = "bob") -> None:
    """Check that bobp installed real skills at Codex's project discovery path."""
    skills_dir = project / ".agents" / "skills"
    if required and not (skills_dir / required / "SKILL.md").is_file():
        raise RuntimeError(
            f"Installed {required.capitalize()} skill was not available at Codex's project-local path."
        )


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


def check_jev_prerequisites() -> str | None:
    """Return an actionable error if the Jev SDK or API key is unavailable."""
    if not os.environ.get("TYPESAFE_API_KEY"):
        return (
            "persona-eval requires a TypeSafe API key for rubric grading. "
            "Set TYPESAFE_API_KEY in your environment and retry."
        )
    try:
        import typesafe_sdk  # noqa: F401
    except ImportError:
        return (
            "persona-eval requires the typesafe-sdk Python package. "
            "Install bobp with its declared dependencies or run `uv sync`."
        )
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


def _fixture_project_context(project: Path) -> str:
    """Summarize fixture capabilities and verifiable paths for the Jev judge."""
    project_declaration = (project / "agents" / "PROJECT.md").read_text(encoding="utf-8")
    available_files = sorted(
        path.relative_to(project).as_posix()
        for path in (project / ".agents" / "skills").rglob("SKILL.md")
    )
    template_root = project / "agents" / "templates"
    if template_root.exists():
        available_files.extend(
            path.relative_to(project).as_posix()
            for path in template_root.glob("*.md")
            if path.is_file()
        )
    docs_root = project / "docs"
    if docs_root.exists():
        available_files.extend(
            path.relative_to(project).as_posix()
            for path in docs_root.rglob("*.md")
            if path.is_file()
        )
    available_files.sort()
    git = shutil.which("git")
    git_worktree_available = False
    if git:
        result = subprocess.run(
            [git, "rev-parse", "--is-inside-work-tree"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        git_worktree_available = result.returncode == 0 and result.stdout.strip() == "true"

    return (
        f"Declared project capabilities:\n{project_declaration}\n\n"
        f"Git executable on PATH: {bool(git)}\n"
        f"Fixture directory is inside a Git worktree: {git_worktree_available}\n"
        "Available project files (paths relative to fixture root):\n"
        + "\n".join(f"- {path}" for path in available_files)
    )


def build_config(
    suite: dict[str, Any],
    project: Path,
    rubric_text: str,
    project_context: str,
    *,
    baseline: bool = False,
    reference_project: Path | None = None,
) -> dict[str, Any]:
    """Build an eval that checks actual installed skill use and artifact quality.

    A baseline config runs the same request without the skill: the sentence that points at the
    skill is dropped from the prompt and the skill-use check is left out. `reference_project`
    is the project that has the skill installed, which the grader still reads the skill text from.
    """
    artifact = suite["artifact"]
    reference = reference_project or project
    request = baseline_request(suite["request"]) if baseline else suite["request"]
    if suite.get("evaluation_scope") == "personality-behavior":
        task = (
            f"{request}\n\n"
            "This is a response-only evaluation. Answer the scenario in your final response; do not "
            "create a deliverable or change your installed skill. Follow required state/chat protocol "
            "only if it applies. Do not commit changes or use network access. Choose routine conventions "
            "without asking the user."
        )
    else:
        task = (
            f"{request}\n\n"
            "Create the requested artifact in the specified path. Do not commit changes "
            "or use network access. Choose routine conventions without asking the user."
        )
    assertion_config: dict[str, Any] = {
        "scenario": suite["request"],
        "artifact_path": str(_project_path(project, artifact)),
        "artifact_relative_path": artifact,
        "project_context": project_context,
        "persona": suite["persona"],
        "rubric_text": rubric_text,
        "persona_skill_text": (
            reference / ".agents" / "skills" / suite["persona"] / "SKILL.md"
        ).read_text(encoding="utf-8"),
    }
    skill_assertion_config = {
        "persona": suite["persona"],
        "expected_skill_text": (
            reference / ".agents" / "skills" / suite["persona"] / "SKILL.md"
        ).read_text(encoding="utf-8"),
    }
    if suite.get("evaluation_scope") == "personality-behavior":
        target_skill_text = (reference / artifact).read_text(encoding="utf-8")
        behavior_criteria = [
            item.strip()
            for item in suite["behavior_criteria"].split(";")
            if item.strip()
        ]
        assertion_config.update(
            {
                "evaluation_scope": "personality-behavior",
                "target_skill_text": target_skill_text,
                "rubric_criteria": [
                    *(
                        {
                            "id": f"behavior_{index}",
                            "label": f"Behavior {index}",
                            "text": f"The persona's final response satisfies this scenario behavior criterion: {text}",
                        }
                        for index, text in enumerate(behavior_criteria, start=1)
                    ),
                ],
            }
        )
    else:
        assertion_config.update(
            {
                "evaluation_scope": "artifact",
                "rubric_criteria": extract_rubric_criteria(rubric_text, suite["request"]),
            }
        )

    jev_assertion = Path(__file__).with_name("persona_eval_jev.py").resolve()
    assertions = [
        {
            "type": "python",
            "value": f"file://{jev_assertion}:grade_with_jev",
            "config": assertion_config,
        },
    ]
    if not baseline:
        assertions.insert(
            0,
            {
                "type": "python",
                "value": f"file://{jev_assertion}:assert_skill_used",
                "config": skill_assertion_config,
            },
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
                "assert": assertions,
            }
        ],
    }


BASELINES = ("none", "without-skill", "previous")


def _execute_promptfoo(
    root: Path, run_dir: Path, config: dict[str, Any], output_path: Path
) -> int | None:
    """Run Promptfoo once for `config`; return its exit code, or None if promptfoo is missing."""
    config_path = run_dir / "promptfooconfig.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    isolated_tmp = run_dir / "tmp"
    isolated_tmp.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "TMPDIR": str(isolated_tmp),
            "TMP": str(isolated_tmp),
            "TEMP": str(isolated_tmp),
            "PROMPTFOO_PYTHON": sys.executable,
        }
    )
    promptfoo = shutil.which("promptfoo")
    if not promptfoo:
        print("The global Promptfoo command is not on PATH. Add npm's global executable directory to PATH and retry.", file=sys.stderr)
        return None
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
    return subprocess.run(command, cwd=root, env=env, check=False).returncode


def _config_name(base: str, attempt: int) -> str:
    """with_skill / without_skill / old_skill for the first attempt, then ..._run2, ..."""
    return base if attempt == 1 else f"{base}_run{attempt}"


def _record_run(
    iteration_dir: Path | None,
    suite: dict[str, Any],
    config_name: str,
    output_path: Path,
    artifact_path: Path | None,
) -> None:
    """Write one run into the workspace; a failure to record is reported, never fatal."""
    if iteration_dir is None:
        return
    try:
        report = json.loads(output_path.read_text(encoding="utf-8"))
        run_dir = iteration_dir / workspace.eval_dir_name(suite["id"]) / config_name
        workspace.write_run(run_dir, report, suite.get("assertions", []), artifact_path)
    except (OSError, ValueError) as exc:
        print(f"Could not record the {config_name} results: {exc}", file=sys.stderr)


def prepare_baseline_project(
    project: Path, temp_root: Path, skill: str, snapshot: Path | None
) -> Path:
    """A fixture project for the baseline run: the skill removed, or replaced by an older version."""
    create_test_project(project)
    install_local_bobp(project, temp_root)
    installed = project / ".agents" / "skills" / skill
    if installed.is_dir() and not installed.is_symlink():
        shutil.rmtree(installed)
    if snapshot is not None:
        shutil.copytree(snapshot, installed, symlinks=True)
    expose_codex_skills(project, required=None)
    return project


def _run_baseline(
    root: Path,
    suite: dict[str, Any],
    reference_project: Path,
    attempt: int,
    run_dir: Path,
    output_dir: Path,
    timestamp: str,
    iteration_dir: Path | None,
    snapshot: Path | None,
) -> None:
    """Run the same request without the skill (or with its previous version) and record it."""
    base_dir = run_dir.with_name(f"{run_dir.name}-baseline")
    base_dir.mkdir()
    project = base_dir / "project"
    prepare_baseline_project(project, base_dir, suite["skill"], snapshot)
    rubric_text = extract_rubric(_project_path(project, suite["rubric"]).read_text())
    config = build_config(
        suite,
        project,
        rubric_text,
        _fixture_project_context(project),
        baseline=True,
        reference_project=reference_project,
    )
    output_path = output_dir / f"{suite['id']}-{timestamp}-run{attempt}-baseline.json"
    returncode = _execute_promptfoo(root, base_dir, config, output_path)
    if returncode is None:
        return
    base = "old_skill" if snapshot is not None else "without_skill"
    _record_run(iteration_dir, suite, _config_name(base, attempt), output_path, None)
    print(f"Baseline ({base}) project: {project}")
    print(f"Baseline report: {output_path}")


def run_suite(
    root: Path,
    suite: dict[str, Any],
    repeat: int = 1,
    *,
    iteration_dir: Path | None = None,
    baseline: str = "none",
    snapshot: Path | None = None,
) -> int:
    """Run repeated, isolated copies of one suite, recording each run in `iteration_dir`.

    With `baseline` "without-skill" the same request is also run with the skill removed;
    with "previous" it is run with `snapshot` (the version evaluated last time) instead,
    falling back to without-skill when there is no snapshot. Baseline results are recorded
    but never fail the suite.
    """
    if baseline not in BASELINES:
        raise ValueError(f"baseline must be one of {', '.join(BASELINES)}")
    if baseline == "previous" and snapshot is None:
        print("No earlier version of this skill was evaluated; using a without-skill baseline.")
        baseline = "without-skill"
    prerequisite_error = check_jev_prerequisites() or check_node_prerequisites()
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
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
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
        project_context = _fixture_project_context(project)
        config = build_config(suite, project, rubric_text, project_context)
        output_path = output_dir / f"{suite['id']}-{timestamp}-run{attempt}.json"
        returncode = _execute_promptfoo(root, run_dir, config, output_path)
        if returncode is None:
            return 2
        if not artifact_path.is_file():
            print(
                f"Eval did not create the expected artifact: {suite['artifact']}",
                file=sys.stderr,
            )
            failures += 1
        if returncode:
            failures += 1
        print(f"Eval project: {project}")
        print(f"Eval report: {output_path}")
        _record_run(
            iteration_dir,
            suite,
            _config_name("with_skill", attempt),
            output_path,
            artifact_path if artifact_path.is_file() else None,
        )
        if baseline != "none":
            _run_baseline(
                root, suite, project, attempt, run_dir, output_dir, timestamp,
                iteration_dir, snapshot if baseline == "previous" else None,
            )
    return 1 if failures else 0


def _snapshot_packaged_skill(skill: str, skill_workspace: Path) -> None:
    """Remember the skill version just evaluated, as installed, for the next 'previous' baseline."""
    from . import _skill_layout

    templates = PACKAGED_AGENTS.parent
    for name, source, is_persona in _skill_layout.template_skills(templates):
        if name != skill:
            continue
        staging = skill_workspace / ".skill-staging"
        if staging.exists():
            shutil.rmtree(staging)
        skill_workspace.mkdir(parents=True, exist_ok=True)
        _skill_layout.build_skill(source, is_persona, staging)
        try:
            workspace.snapshot_skill(staging, skill_workspace)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        return


def _finish_iteration(output_dir: Path, skill: str, iteration_dir: Path) -> None:
    """Write the iteration's benchmark.json, print it, and snapshot the evaluated skill."""
    skill_workspace = workspace.workspace_dir(output_dir, skill)
    try:
        benchmark = workspace.write_benchmark(iteration_dir)
    except ValueError as exc:
        print(f"No benchmark for {iteration_dir.name}: {exc}", file=sys.stderr)
        if not any(iteration_dir.iterdir()):
            iteration_dir.rmdir()  # a run that recorded nothing should not use up a number
        return
    print(f"\nBenchmark for {skill} ({iteration_dir.name}): {iteration_dir / 'benchmark.json'}")
    for name, stats in benchmark["run_summary"].items():
        if name == "delta":
            print(f"  delta vs baseline: {json.dumps(stats)}")
        else:
            print(
                f"  {name}: pass_rate {stats['pass_rate']['mean']} "
                f"(±{stats['pass_rate']['stddev']}), "
                f"{stats['time_seconds']['mean']}s, {stats['tokens']['mean']} tokens"
            )
    _snapshot_packaged_skill(skill, skill_workspace)


def select_suites(suites: list[dict[str, Any]], selector: str) -> list[dict[str, Any]]:
    """Select suites by persona name or exact suite id."""
    return [suite for suite in suites if selector in (suite["id"], suite["persona"])]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run the Promptfoo skill-use and artifact evaluations in each skill's evals/evals.json."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("selector", nargs="?", help="Persona name or eval suite id.")
    group.add_argument("--all", action="store_true", help="Run every suite in the catalog.")
    group.add_argument("--list", action="store_true", help="List the evaluation cases.")
    group.add_argument("--setup", action="store_true", help="Show instructions for installing locked npm dependencies globally.")
    parser.add_argument("--repeat", type=int, default=1, help="Fresh runs per suite (default: 1).")
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --list: print the cases as a JSON array on stdout and nothing else.",
    )
    parser.add_argument(
        "--baseline",
        choices=BASELINES,
        default="none",
        help=(
            "Also run each case for comparison: 'without-skill' removes the skill, 'previous' runs "
            "the version evaluated last time (falls back to without-skill). Doubles the number of "
            "Codex and Jev calls. Default: none."
        ),
    )
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    if args.json and not args.list:
        parser.error("--json can only be used with --list")

    try:
        root = find_project_root()
        suites = load_evals()
    except ValueError as exc:
        parser.error(str(exc))

    if args.setup:
        raise SystemExit(show_node_setup_instructions())

    if args.list:
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "suite": suite["id"],
                            "persona": suite["persona"],
                            "skill": suite["skill"],
                            "tags": suite.get("tags", []),
                        }
                        for suite in suites
                    ]
                )
            )
            return
        for suite in suites:
            print(f"{suite['id']}\t{suite['persona']}\t{', '.join(suite.get('tags', []))}")
        return

    if args.all:
        selected = suites
    else:
        selected = select_suites(suites, args.selector)
        if not selected:
            parser.error(f"No eval suites found for '{args.selector}'. Use --list to see the catalog.")

    output_dir = root / "build" / "persona-eval"
    iterations: dict[str, Path] = {}
    snapshots: dict[str, Path | None] = {}
    failures = []
    for suite in selected:
        skill = suite["skill"]
        if skill not in iterations:
            skill_workspace = workspace.workspace_dir(output_dir, skill)
            snapshots[skill] = workspace.previous_snapshot(skill_workspace)
            iterations[skill] = workspace.make_iteration(skill_workspace)
            print(f"\nRecording {skill} results in {iterations[skill]} (baseline: {args.baseline})")
        print(f"\n=== Eval suite: {suite['id']} ===", flush=True)
        code = run_suite(
            root,
            suite,
            args.repeat,
            iteration_dir=iterations[skill],
            baseline=args.baseline,
            snapshot=snapshots[skill],
        )
        if code:
            failures.append((suite["id"], code))
    for skill, iteration_dir in iterations.items():
        _finish_iteration(output_dir, skill, iteration_dir)
    if failures:
        for suite_id, code in failures:
            print(f"FAIL {suite_id} (Promptfoo exit {code})", file=sys.stderr)
        raise SystemExit(1)
    print("\nPASS: all selected eval suites passed.")


if __name__ == "__main__":
    main()
