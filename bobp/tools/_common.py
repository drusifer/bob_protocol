"""Shared helpers for bobp.tools scripts.

TLDR:
    find_project_root() locates the project a bobp tool is operating on by
    walking upward from the current working directory looking for an
    agents/ directory. Tool scripts used to derive this from __file__
    (assuming they lived at <project>/agents/tools/<script>.py); once they
    ship as installed package modules under bobp/tools/, __file__ points
    into site-packages instead, so cwd-based discovery is the only option
    that works both in editable dev installs and real installs.
    find_persona_dirs() lists the persona folders, agents/<name>/, identified
    by the state.md they hold (or, in older projects, a SKILL.md).
"""

import os
import sys
import tempfile
from pathlib import Path


# One-line file in <project>/agents/ recording which bobp last set the project up.
STAMP_NAME = ".bobp-version"
EXIT_CODES_EPILOG = (
    "Exit codes:\n"
    "  0  Success\n"
    "  1  Failure\n"
    "  2  Invalid usage or confirmation required\n"
)


def write_text_safely(path: Path, text: str) -> None:
    """Write `text` to `path` without ever writing through a symlink at `path`.

    The project may be a cloned repository that planted a symlink where bobp
    writes (SEC-006). The text goes to a fresh, randomly named file in the same
    directory (created exclusively), which is then renamed over `path`; a rename
    replaces a symlink itself and never its target, and readers never see a
    half-written file.
    """
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def find_project_root_or_none(start: "Path | None" = None) -> "Path | None":
    """Walk upward from `start` (default: cwd) for a directory containing agents/."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "agents").is_dir():
            return candidate
    return None


def find_project_root(start: "Path | None" = None) -> Path:
    """Like find_project_root_or_none, but exit with an error when there is no project."""
    root = find_project_root_or_none(start)
    if root is None:
        current = (start or Path.cwd()).resolve()
        print(f"Error: Could not find agents/ directory from {current}", file=sys.stderr)
        sys.exit(1)
    return root


# Directories under agents/ that are never personas.
NON_PERSONA_DIRS = frozenset({"skills", "templates", "chat_archive", "tools"})


def find_persona_dirs(agents_dir: Path) -> list[tuple[str, Path]]:
    """Find persona folders: agents/<name>/ directories holding persona memory.

    A persona's memory (state.md) lives in agents/<name>/; its SKILL.md lives in
    .claude/skills/<name>/. A folder that still holds a SKILL.md (older layout)
    also counts, so a project can be found before it is migrated.
    """
    personas = []
    for item in sorted(agents_dir.iterdir()):
        if item.name in NON_PERSONA_DIRS or item.name.startswith("."):
            continue
        if item.is_dir() and ((item / "state.md").exists() or (item / "SKILL.md").exists()):
            personas.append((item.name, item))
    return personas
