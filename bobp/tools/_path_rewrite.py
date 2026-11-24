"""Rewrite references to the old skill locations in a project's instruction files.

TLDR:
    Skills moved from agents/skills/<name>/ and agents/<persona>/SKILL.md to
    .agents/skills/<name>/SKILL.md, and agents/AGENTS.md to AGENTS.md at the
    project root. rewrite_text() applies exact old-path -> new-path replacements;
    rewrite_files() applies them to regular, small, UTF-8 documentation files
    (.md, .txt, .template), never through a symlink; project_targets() is the
    deliberately short list of files `bobp update` rewrites: the root AGENTS.md,
    agents/templates/, agents/PROJECT.md, agents/DOCUMENTATION_INDEX.md,
    agents/*/HELP.md and the project's own skills. Persona memory, lessons,
    findings, sprint documents and chat history are history, not instructions,
    and are never touched.

    This is code, not a shell one-liner (project principle 11): it is tested,
    idempotent, and the same function migrates the packaged templates and every
    project. The old paths are matched only when not part of a longer path or
    word. Intermediate `.claude/skills/` references are rewritten only when
    explicitly requested during migration of Bob Protocol owned content.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Iterator

from ._common import write_text_safely

PERSONAS = (
    "bob", "cypher", "morpheus", "mouse", "neo", "oracle", "smith", "switch", "tank", "trin",
)
SUFFIXES = (".md", ".txt", ".template")
SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "build", "chat_archive", "__pycache__"})
SKIP_NAMES = frozenset({"CHAT.md", "CHAT.diagram.md"})
MAX_FILE_BYTES = 1024 * 1024

_PLACEHOLDERS = r"\[persona\]|\[name\]|<persona>|<name>|<agent>|\{persona\}|\*"
_BEFORE = r"(?<![\w./-])"  # a repo-relative path start, not the tail of a longer path or name


def _rules(personas: Iterable[str], intermediate: bool = False) -> "list[tuple[re.Pattern[str], str]]":
    names = "|".join(re.escape(name) for name in dict.fromkeys(personas))
    alternatives = f"{names}|{_PLACEHOLDERS}" if names else _PLACEHOLDERS
    rules = [
        (re.compile(_BEFORE + r"agents/skills(?![\w-])"), ".agents/skills"),
        (re.compile(_BEFORE + rf"agents/({alternatives})/SKILL\.md"), r".agents/skills/\1/SKILL.md"),
        (re.compile(_BEFORE + r"agents/AGENTS\.md"), "AGENTS.md"),
    ]
    if intermediate:
        rules.append((re.compile(_BEFORE + r"\.claude/skills(?![\w-])"), ".agents/skills"))
    return rules


# Relative links written inside a skill file. Personas and shared skills used to sit in
# different folders (agents/<persona>/ and agents/skills/<skill>/); now both are siblings
# in .agents/skills/, and the artifact templates are three levels up in agents/templates/.
_SKILL_LINK_RULES = [
    (re.compile(r"\]\(\.\./skills/"), "](../"),
    (re.compile(r"`\.\./skills/"), "`../"),
    (re.compile(r"\]\(\.\./(?:\.\./)?templates/"), "](../../../agents/templates/"),
]

# Skill-like files: a skill's SKILL.md (installed or packaged) and the persona scaffold,
# whose example links are meant to be pasted into a persona skill.
SKILL_FILE_NAMES = frozenset({"SKILL.md", "SKILL.md.txt", "_template_PERSONA_SKILL.md"})


def rewrite_text(
    text: str,
    personas: Iterable[str],
    root_agents_md: bool = False,
    in_skill: bool = False,
    intermediate: bool = False,
) -> str:
    """Apply the old -> new path replacements to `text`.

    `root_agents_md` is for the instructions file that moved from agents/ to the project
    root: its links that climbed out of agents/ (`](../docs/...`) now start at the root.
    `in_skill` is for a skill file, whose relative links to other skills and to the artifact
    templates change because of where skills now live.
    """
    for pattern, replacement in _rules(personas, intermediate):
        text = pattern.sub(replacement, text)
    if in_skill:
        for pattern, replacement in _SKILL_LINK_RULES:
            text = pattern.sub(replacement, text)
    if root_agents_md:
        text = text.replace("](../", "](")
    return text


def walk(root: Path) -> Iterator[Path]:
    """Regular documentation files under `root`, skipping history/tooling dirs and symlinks."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in SKIP_DIRS and not (Path(dirpath) / name).is_symlink()
        )
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if name in SKIP_NAMES or not name.endswith(SUFFIXES) or path.is_symlink():
                continue
            if path.is_file():
                yield path


def rewrite_files(
    paths: Iterable[Path], personas: Iterable[str], dry_run: bool = False,
    intermediate: bool = False,
) -> "list[Path]":
    """Rewrite each regular documentation file; return those that changed (or would)."""
    personas = tuple(personas)
    changed: "list[Path]" = []
    for path in paths:
        try:
            if path.is_symlink() or not path.is_file() or not path.name.endswith(SUFFIXES):
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        updated = rewrite_text(
            original,
            personas,
            root_agents_md=path.name == "AGENTS.md",
            in_skill=path.name in SKILL_FILE_NAMES,
            intermediate=intermediate,
        )
        if updated == original:
            continue
        changed.append(path)
        if not dry_run:
            write_text_safely(path, updated)
    return changed


def project_targets(project: Path, owned: "set[str]") -> "list[Path]":
    """The files `bobp update` rewrites in a project (see the module docstring)."""
    targets: "list[Path]" = []

    def add(path: Path) -> None:
        if path.is_file() and not path.is_symlink() and path not in targets:
            targets.append(path)

    add(project / "AGENTS.md")
    agents = project / "agents"
    if agents.is_dir() and not agents.is_symlink():
        templates = agents / "templates"
        if templates.is_dir() and not templates.is_symlink():
            for path in walk(templates):
                add(path)
        add(agents / "PROJECT.md")
        add(agents / "DOCUMENTATION_INDEX.md")
        for child in sorted(agents.iterdir()):
            if child.is_dir() and not child.is_symlink():
                add(child / "HELP.md")
    dot_agents = project / ".agents"
    skills = dot_agents / "skills"
    if not dot_agents.is_symlink() and skills.is_dir() and not skills.is_symlink():
        for child in sorted(skills.iterdir()):
            if child.name not in owned and child.is_dir() and not child.is_symlink():
                for path in walk(child):
                    add(path)
    return targets
