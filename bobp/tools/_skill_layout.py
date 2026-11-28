"""Where Bob Protocol skills live in a project, and how they get there.

TLDR:
    Every persona and shared skill is an ordinary Agent Skills directory,
    .agents/skills/<name>/SKILL.md (https://agentskills.io/specification), copied
    in as real files - never symlinked. place_skills() installs or refreshes
    them from the packaged templates. Persona memory (state.md, lessons, ...)
    stays in agents/<persona>/ and is not part of a skill. .agents/skills/ is the
    location Codex, Cursor, Copilot and Gemini CLI read; Claude Code reads only
    .claude/skills/, which bobp no longer writes to.

    Ownership: agents/.bobp-skills lists the skills bobp placed. Update only
    replaces a directory it owns (or a legacy bobp symlink that points into the
    project's agents/ directory); a skill the project made itself, even one with
    a colliding name, is left alone and reported.

    Safety: a project may be a cloned repository, so its .agents directory,
    skills directory and manifest are untrusted. A symlinked .agents or
    .agents/skills is refused (an older bobp linked .agents -> agents; update
    removes that link first); the manifest is read as a small regular file
    without following links or blocking, and every name in it is validated
    against the Agent Skills name rule before it is used as a path.
"""

import os
import re
import shutil
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from ._common import write_text_safely

SKILLS_DIR = Path(".agents") / "skills"
# Where Claude Code itself looks. Older bobp versions linked skills here, and an
# unreleased intermediate layout placed real copies here; both are cleaned up.
CLAUDE_SKILLS_DIR = Path(".claude") / "skills"
MANIFEST_NAME = ".bobp-skills"
MAX_MANIFEST_BYTES = 64 * 1024
MAX_NAME_LENGTH = 64

_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Files and folders of a packaged persona that belong to the skill (the rest,
# state.md and friends, is persona memory and stays in agents/<persona>/).
_PERSONA_SKILL_PARTS = ("evals", "references")


class SkillLayoutError(Exception):
    """The project layout cannot be written safely."""


@dataclass(frozen=True)
class Action:
    """One thing place_skills did (or, in a dry run, would do)."""

    kind: str  # create | replace | skipped
    path: str  # project-relative, posix style
    note: str = ""


def valid_name(name: str) -> bool:
    """Agent Skills name rule: lowercase letters, digits, single hyphens, <= 64 chars."""
    return bool(name) and len(name) <= MAX_NAME_LENGTH and _NAME_RE.match(name) is not None


def skills_root(project: Path) -> Path:
    return project / SKILLS_DIR


def _check_writable_root(project: Path) -> Path:
    """Return the skills directory, refusing to write through a symlinked parent."""
    for part in (project / SKILLS_DIR.parent, skills_root(project)):
        if part.is_symlink():
            raise SkillLayoutError(f"{part} is a symlink; refusing to write skills through it.")
        if part.exists() and not part.is_dir():
            raise SkillLayoutError(f"{part} exists and is not a directory.")
    return skills_root(project)


def read_manifest(agents_dir: Path) -> "set[str]":
    """Names of the skills bobp placed here. Missing, unreadable or hostile -> empty/partial."""
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(agents_dir / MANIFEST_NAME, flags)
    except OSError:
        return set()
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return set()
        raw = os.read(fd, MAX_MANIFEST_BYTES)
    except OSError:
        return set()
    finally:
        os.close(fd)
    names = (line.strip() for line in raw.decode("utf-8", errors="replace").splitlines())
    return {name for name in names if valid_name(name)}


def write_manifest(agents_dir: Path, names: "set[str]") -> None:
    """Write the manifest atomically (replacing a symlink in its place, never writing through it)."""
    agents_dir.mkdir(parents=True, exist_ok=True)
    write_text_safely(
        agents_dir / MANIFEST_NAME, "".join(f"{name}\n" for name in sorted(names))
    )


def template_skills(tmpl: Path) -> "list[tuple[str, Path, bool]]":
    """(name, source, is_persona) for everything the packaged templates ship as a skill.

    A persona's source is its SKILL.md.txt; a shared skill's source is its directory.
    """
    found = [
        (path.parent.name, path, True)
        for path in sorted((tmpl / "agents").glob("*/SKILL.md.txt"))
    ]
    shared = tmpl / "agents" / "skills"
    if shared.is_dir():
        found += [
            (child.name, child, False)
            for child in sorted(shared.iterdir())
            if (child / "SKILL.md.txt").is_file()
        ]
    return found


def persona_names(tmpl: Path) -> "list[str]":
    return [name for name, _, is_persona in template_skills(tmpl) if is_persona]


def _points_into_agents(link: Path, project: Path) -> bool:
    """True if `link` is a symlink whose literal target is inside <project>/agents (no following)."""
    try:
        target = os.readlink(link)
    except OSError:
        return False
    resolved = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(link)), target))
    agents = os.path.normpath(os.path.join(os.path.abspath(project), "agents"))
    return resolved == agents or resolved.startswith(agents + os.sep)


def build_skill(src: Path, is_persona: bool, dest: Path) -> None:
    """Copy one skill from the templates into `dest` as real files."""
    if is_persona:
        dest.mkdir(parents=True)
        shutil.copyfile(src, dest / "SKILL.md")
        for part in _PERSONA_SKILL_PARTS:
            extra = src.parent / part
            if extra.is_dir():
                shutil.copytree(extra, dest / part)
        return
    shutil.copytree(src, dest, symlinks=False)
    (dest / "SKILL.md.txt").rename(dest / "SKILL.md")


def _relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def place_skills(project: Path, tmpl: Path, dry_run: bool = False) -> "list[Action]":
    """Install or refresh every packaged persona and shared skill under .agents/skills/."""
    root = _check_writable_root(project)
    agents_dir = project / "agents"
    owned = read_manifest(agents_dir)
    installed = set(owned)
    actions: "list[Action]" = []

    for name, src, is_persona in template_skills(tmpl):
        if not valid_name(name):
            actions.append(Action("skipped", name, "not a valid skill name"))
            continue
        dest = root / name
        rel = _relative(project, dest)
        if dest.is_symlink():
            if not _points_into_agents(dest, project):
                actions.append(Action("skipped", rel, "symlink not created by bobp"))
                continue
            kind, note = "replace", "legacy bobp link replaced by a real directory"
        elif dest.exists():
            if not dest.is_dir() or name not in owned:
                actions.append(Action("skipped", rel, "exists and was not installed by bobp"))
                continue
            kind, note = "replace", ""
        else:
            kind, note = "create", ""

        actions.append(Action(kind, rel, note))
        installed.add(name)
        if dry_run:
            continue

        root.mkdir(parents=True, exist_ok=True)
        staging = root / f".{name}.bobp-new"
        if staging.is_symlink() or staging.is_file():
            staging.unlink()
        elif staging.is_dir():
            shutil.rmtree(staging)
        build_skill(src, is_persona, staging)
        if dest.is_symlink():
            dest.unlink()
        elif dest.exists():
            shutil.rmtree(dest)
        os.replace(staging, dest)

    if not dry_run and agents_dir.is_dir():
        write_manifest(agents_dir, installed)
    return actions


# Links older bobp versions created inside a project. A link is removed only if
# its literal target is inside the project's agents/ directory.
LEGACY_LINKS = (
    ".agents",
    "AGENT.md",
    "GEMINI.md",
    ".cursorrules",
    "CHATGPT.md",
    ".github/copilot-instructions.md",
    "agents/AGENT.md",
)


def remove_legacy_links(project: Path, dry_run: bool = False) -> "list[Action]":
    """Remove the symlinks older bobp versions created; never touch anything else.

    Real files and directories are never touched. A symlink is removed only when
    its literal target (read without following it) lies inside <project>/agents;
    any other symlink is left and reported. Nothing is done through a symlinked
    parent directory.
    """
    actions: "list[Action]" = []
    removed_copilot = False
    for rel in LEGACY_LINKS:
        link = project / rel
        if link.parent != project and link.parent.is_symlink():
            continue
        if not link.is_symlink():
            continue
        if not _points_into_agents(link, project):
            actions.append(Action("skipped", rel, "symlink not created by bobp"))
            continue
        actions.append(Action("remove", rel, "legacy link"))
        removed_copilot = removed_copilot or rel.startswith(".github/")
        if not dry_run:
            link.unlink()

    claude = project / CLAUDE_SKILLS_DIR.parent
    skills = project / CLAUDE_SKILLS_DIR
    if not claude.is_symlink() and skills.is_symlink() and _points_into_agents(skills, project):
        # An older bobp linked the whole directory (.claude/skills -> agents/skills).
        actions.append(Action("remove", _relative(project, skills), "legacy skills directory link"))
        if not dry_run:
            skills.unlink()
    if not claude.is_symlink() and skills.is_dir() and not skills.is_symlink():
        for child in sorted(skills.iterdir()):
            if child.is_symlink() and _points_into_agents(child, project):
                actions.append(Action("remove", _relative(project, child), "legacy skill link"))
                if not dry_run:
                    child.unlink()

    github = project / ".github"
    if removed_copilot and not dry_run and github.is_dir() and not github.is_symlink():
        if not any(github.iterdir()):
            github.rmdir()
    return actions


def remove_claude_skill_copies(
    project: Path, owned: "set[str]", dry_run: bool = False
) -> "list[Action]":
    """Remove the real copies of bobp's own skills left in .claude/skills/ by an earlier layout.

    Only directories named in the ownership manifest are removed, and only real
    directories (never symlinks); a skill the project keeps there for Claude Code
    itself is not bobp's and stays.
    """
    actions: "list[Action]" = []
    claude = project / CLAUDE_SKILLS_DIR.parent
    skills = project / CLAUDE_SKILLS_DIR
    if claude.is_symlink() or skills.is_symlink() or not skills.is_dir():
        return actions
    for name in sorted(owned):
        copy = skills / name
        if copy.is_symlink() or not copy.is_dir():
            continue
        actions.append(
            Action("remove", _relative(project, copy), "moved to .agents/skills/")
        )
        if not dry_run:
            shutil.rmtree(copy)
    if not dry_run and not any(skills.iterdir()):
        skills.rmdir()
    return actions


def migrate_legacy(project: Path, tmpl: Path, dry_run: bool = False) -> "list[Action]":
    """Move skills out of the older agents/ layout into .agents/skills/.

    A packaged skill's old copy is deleted (the fresh one is placed afterwards).
    A skill the project made itself is moved and left unowned, so a later update
    never overwrites it. Nothing is done through a symlinked agents/ or
    agents/skills/, and an existing destination is never overwritten.
    """
    agents = project / "agents"
    actions: "list[Action]" = []
    if agents.is_symlink() or not agents.is_dir():
        return actions
    packaged = {name for name, _, _ in template_skills(tmpl)}
    packaged_personas = set(persona_names(tmpl))
    root = skills_root(project)

    def destination(name: str) -> "Path | None":
        if not valid_name(name):
            actions.append(Action("skipped", f"agents/{name}", "not a valid skill name"))
            return None
        dest = root / name
        if os.path.lexists(dest):
            actions.append(Action("skipped", _relative(project, dest), "already exists; merge by hand"))
            return None
        return dest

    shared = agents / "skills"
    if shared.is_symlink():
        actions.append(Action("skipped", "agents/skills", "is a symlink; not touched"))
    elif shared.is_dir():
        for child in sorted(shared.iterdir()):
            if child.is_symlink() or not child.is_dir() or not (child / "SKILL.md").is_file():
                continue
            rel = _relative(project, child)
            if child.name in packaged:
                actions.append(Action("remove", rel, "old copy of a packaged skill"))
                if not dry_run:
                    shutil.rmtree(child)
                continue
            dest = destination(child.name)
            if dest is None:
                continue
            actions.append(Action("move", rel, f"-> {_relative(project, dest)}"))
            if not dry_run:
                _check_writable_root(project)
                root.mkdir(parents=True, exist_ok=True)
                os.replace(child, dest)
        if not dry_run and not any(shared.iterdir()):
            shared.rmdir()

    for persona_dir in sorted(agents.iterdir()):
        skill = persona_dir / "SKILL.md"
        if (
            persona_dir.is_symlink()
            or not persona_dir.is_dir()
            or skill.is_symlink()
            or not skill.is_file()
        ):
            continue
        rel = _relative(project, skill)
        if persona_dir.name in packaged_personas:
            actions.append(Action("remove", rel, "old copy of a packaged persona skill"))
            if not dry_run:
                skill.unlink()
            continue
        dest = destination(persona_dir.name)
        if dest is None:
            continue
        actions.append(Action("move", rel, f"-> {_relative(project, dest / 'SKILL.md')}"))
        if not dry_run:
            _check_writable_root(project)
            dest.mkdir(parents=True)
            os.replace(skill, dest / "SKILL.md")
    return actions


MAX_AGENTS_MD_BYTES = 1024 * 1024
BOB_AGENTS_MD = Path("agents") / "BOB_AGENTS.md"
ROOT_AGENTS_POINTER_TEXT = (
    "# Project Agent Instructions\n\n"
    "Read and follow [`agents/BOB_AGENTS.md`](agents/BOB_AGENTS.md) for all Bob Protocol "
    "operating rules, state management, persona roster, and core principles.\n\n"
    "<!-- Add project-specific instructions below; `bobp update` never overwrites this file. -->\n"
)


def _read_regular(path: Path) -> "str | None":
    """Text of a regular, small file (not a symlink), else None."""
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_AGENTS_MD_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def place_bob_agents_md(project: Path, tmpl: Path, dry_run: bool = False) -> "list[Action]":
    """Install or refresh bobp-owned `agents/BOB_AGENTS.md` from packaged templates.

    Unlike root `AGENTS.md` (owned by the project), `agents/BOB_AGENTS.md` is owned
    by bobp and always updated so upgrades deliver new Bob Protocol operating rules.
    Refuses to write through a symlinked `agents/` or symlinked/non-regular target.
    """
    agents_dir = project / "agents"
    if agents_dir.is_symlink():
        raise SkillLayoutError(
            f"{printable(str(agents_dir))} is a symlink; refusing to write BOB_AGENTS.md through it."
        )
    if agents_dir.exists() and not agents_dir.is_dir():
        raise SkillLayoutError(f"{printable(str(agents_dir))} exists and is not a directory.")

    dest = project / BOB_AGENTS_MD
    if dest.is_symlink():
        raise SkillLayoutError(
            f"{printable(str(dest))} is a symlink; refusing to overwrite it."
        )
    if dest.exists() and not dest.is_file():
        raise SkillLayoutError(f"{printable(str(dest))} exists and is not a regular file.")

    packaged = (tmpl / BOB_AGENTS_MD).read_text(encoding="utf-8")
    rel = BOB_AGENTS_MD.as_posix()
    kind = "replace" if dest.exists() else "write"
    note = "refreshed Bob Protocol instructions" if kind == "replace" else "Bob Protocol instructions"
    if not dry_run:
        agents_dir.mkdir(parents=True, exist_ok=True)
        write_text_safely(dest, packaged)
    return [Action(kind, rel, note)]


def ensure_root_agents_md(project: Path, tmpl: Path, dry_run: bool = False) -> "list[Action]":
    """Ensure project-owned `<project>/AGENTS.md` exists and points to `agents/BOB_AGENTS.md`.

    - missing: written as a minimal starter pointer to `agents/BOB_AGENTS.md`;
    - a legacy symlink to `agents/AGENTS.md`: replaced by a regular file with the same text
      (or the starter pointer when dangling);
    - an existing regular file: left untouched (notes if it does not reference `agents/BOB_AGENTS.md`);
    - a symlink anywhere else: left alone and reported.
    A leftover `agents/AGENTS.md` is removed when it matches the root file and kept
    (and reported) when it differs.
    """
    del tmpl  # Root starter text is ROOT_AGENTS_POINTER_TEXT; full rules live in agents/BOB_AGENTS.md.
    root = project / "AGENTS.md"
    legacy = project / "agents" / "AGENTS.md"
    actions: "list[Action]" = []

    if root.is_symlink():
        if not _points_into_agents(root, project):
            actions.append(Action("skipped", "AGENTS.md", "symlink not created by bobp"))
            return actions
        text = _read_regular(legacy)
        actions.append(Action("convert", "AGENTS.md", "legacy link replaced by a real file"))
        if not dry_run:
            write_text_safely(root, text if text is not None else ROOT_AGENTS_POINTER_TEXT)
        if text is not None:
            actions.append(Action("remove", "agents/AGENTS.md", "content moved to AGENTS.md"))
            if not dry_run:
                legacy.unlink()
        return actions

    if not os.path.lexists(root):
        actions.append(Action("write", "AGENTS.md", "starter pointer to agents/BOB_AGENTS.md"))
        if not dry_run:
            write_text_safely(root, ROOT_AGENTS_POINTER_TEXT)
        return actions

    root_text = _read_regular(root)
    legacy_text = _read_regular(legacy)
    if root_text is not None and legacy_text is not None:
        if legacy_text == root_text:
            actions.append(Action("remove", "agents/AGENTS.md", "same as AGENTS.md"))
            if not dry_run:
                legacy.unlink()
        else:
            actions.append(
                Action("skipped", "agents/AGENTS.md", "differs from AGENTS.md; merge by hand")
            )
    if root_text is not None and "agents/BOB_AGENTS.md" not in root_text:
        actions.append(
            Action(
                "note",
                "AGENTS.md",
                "does not mention agents/BOB_AGENTS.md; add a pointer so upgraded Bob Protocol rules are read",
            )
        )
    return actions


_HIDING_GITIGNORE_LINES = frozenset(
    {".agents", ".agents/", "/.agents", "/.agents/", ".agents/*", "/.agents/*"}
)


def gitignore_hides_skills(project: Path) -> bool:
    """True if the project's .gitignore ignores all of .agents/, so its skills would not be committed."""
    text = _read_regular(project / ".gitignore")
    if text is None:
        return False
    return any(line.strip() in _HIDING_GITIGNORE_LINES for line in text.splitlines())


def legacy_codex_links(project: Path, codex_home: Path) -> "list[Path]":
    """Codex-home skill links older bobp versions made for this project (read-only listing)."""
    skills = codex_home / "skills"
    try:
        if not skills.is_dir():
            return []
        return [
            child
            for child in sorted(skills.iterdir())
            if child.is_symlink() and _points_into_agents(child, project)
        ]
    except OSError:
        return []


_VERBS = {
    "remove": "Removed",
    "move": "Moved",
    "convert": "Converted",
    "write": "Wrote",
    "replace": "Updated",
    "note": "Note",
    "skipped": "Skipped",
}


def printable(text: str, limit: int = 200) -> str:
    """Drop control and format characters and cap the length, for text echoed to a terminal.

    Names come from the project, which may be a cloned repository (SEC-007).
    """
    cleaned = "".join(ch for ch in text if not unicodedata.category(ch).startswith("C"))
    return cleaned if len(cleaned) <= limit else cleaned[:limit] + "..."


def describe(actions: "list[Action]") -> "list[str]":
    """One line per migration/cleanup action (skill placement has its own summary)."""
    return [
        f"  {_VERBS[a.kind]} {printable(a.path)}" + (f": {printable(a.note)}" if a.note else "")
        for a in actions
        if a.kind in _VERBS
    ]


def summarize(actions: "list[Action]") -> "list[str]":
    """Short human-readable lines for what place_skills did."""
    counts = {"create": 0, "replace": 0, "skipped": 0}
    for action in actions:
        counts[action.kind] += 1
    lines = [
        f"Skills in {SKILLS_DIR.as_posix()}/: {counts['create']} added, "
        f"{counts['replace']} refreshed, {counts['skipped']} skipped."
    ]
    lines += [
        f"  skipped {printable(a.path)}: {printable(a.note)}"
        for a in actions
        if a.kind == "skipped"
    ]
    return lines
