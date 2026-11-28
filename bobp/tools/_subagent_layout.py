"""Compile and manage harness-native subagent definitions for Bob Protocol personas.

TLDR:
    Single source of truth is the 10 packaged persona SKILL.md.txt files.
    place_subagents() compiles and writes 30 real project-local subagent files
    (never symlinks) across:
      - Claude Code: .claude/agents/<persona>.md  (YAML frontmatter + Markdown)
      - OpenAI Codex: .codex/agents/<persona>.toml (TOML with developer_instructions)
      - Gemini CLI:  .gemini/agents/<persona>.md  (YAML frontmatter with kind: local)

    Every generated subagent directs the persona to the single shared project
    memory at agents/<persona>/state.md and agents/CHAT.md (no harness-private
    memory, no hardcoded model pins, inherited tools).

    Ownership: agents/.bobp-subagents tracks bobp-owned relative paths. Custom
    user subagents are never overwritten. All reads/writes enforce parent-chain
    symlink checks, O_NOFOLLOW | O_NONBLOCK regular-file reads with fail-closed
    size caps (SEC-005), atomic writes (SEC-006), and terminal output
    sanitization (SEC-007).
"""

import os
import re
import stat
from pathlib import Path

from . import _skill_layout
from ._common import write_text_safely
from ._skill_layout import Action, printable, valid_name

HARNESS_SPECS: "dict[str, tuple[str, str]]" = {
    "claude": (".claude/agents", ".md"),
    "codex": (".codex/agents", ".toml"),
    "gemini": (".gemini/agents", ".md"),
}
HARNESS_ORDER: "tuple[str, ...]" = ("claude", "codex", "gemini")
MANIFEST_NAME = ".bobp-subagents"
MAX_MANIFEST_BYTES = 64 * 1024
MAX_GITIGNORE_BYTES = 256 * 1024
MAX_SUBAGENT_BYTES = 1024 * 1024
MAX_RELPATH_LEN = 128

_TRIPLE_QUOTES_RE = re.compile(r'"{3,}')


class SubagentLayoutError(Exception):
    """The project's harness subagent directories or manifest cannot be used safely."""


def _check_dir_chain(root: Path, rel_parts: "tuple[str, ...]", *, must_exist: bool = False) -> None:
    """Verify every directory component in `rel_parts` under `root` is not a symlink or non-dir."""
    current = root
    for part in rel_parts:
        current = current / part
        try:
            st = os.lstat(current)
        except FileNotFoundError:
            if must_exist:
                raise SubagentLayoutError(f"{printable(str(current))} does not exist.")
            return
        except OSError as exc:
            raise SubagentLayoutError(
                f"Cannot inspect {printable(str(current))}: {printable(str(exc))}"
            ) from exc
        if stat.S_ISLNK(st.st_mode):
            raise SubagentLayoutError(
                f"{printable(str(current))} is a symlink; refusing to write subagents through it."
            )
        if not stat.S_ISDIR(st.st_mode):
            raise SubagentLayoutError(
                f"{printable(str(current))} exists and is not a directory."
            )


def _dir_chain_is_safe(root: Path, rel_parts: "tuple[str, ...]") -> bool:
    """Boolean wrapper around _check_dir_chain for non-fatal read paths (diff/pull)."""
    try:
        _check_dir_chain(root, rel_parts)
    except SubagentLayoutError:
        return False
    return True


def _read_regular_safe(root: Path, rel_path: str, max_bytes: int) -> "str | None":
    """Read a regular UTF-8 file under `root` without following symlinks or blocking.

    Verifies every parent directory component is a non-symlink directory, opens
    the leaf with O_NOFOLLOW | O_NONBLOCK, checks S_ISREG, and fails closed if
    the file exceeds `max_bytes` or contains invalid UTF-8.
    """
    parts = tuple(p for p in rel_path.split("/") if p)
    if not parts or any(p in (".", "..") for p in parts):
        return None
    if len(parts) > 1 and not _dir_chain_is_safe(root, parts[:-1]):
        return None
    target = root.joinpath(*parts)
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        chunks: list[bytes] = []
        total = 0
        limit = max_bytes + 1
        while total < limit:
            chunk = os.read(fd, min(65536, limit - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if total > max_bytes:
            return None
        raw = b"".join(chunks)
    except OSError:
        return None
    finally:
        os.close(fd)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _preflight(project: Path) -> None:
    """Validate agents/, all 3 harness dir chains, and agents/.bobp-subagents before ANY write."""
    _check_dir_chain(project, ("agents",))
    for harness in HARNESS_ORDER:
        hdir, _ = HARNESS_SPECS[harness]
        _check_dir_chain(project, tuple(hdir.split("/")))

    manifest_path = project / "agents" / MANIFEST_NAME
    try:
        st = os.lstat(manifest_path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise SubagentLayoutError(
            f"Cannot inspect {printable(str(manifest_path))}: {printable(str(exc))}"
        ) from exc
    if stat.S_ISLNK(st.st_mode):
        raise SubagentLayoutError(
            f"{printable(str(manifest_path))} is a symlink; refusing to read or overwrite it."
        )
    if not stat.S_ISREG(st.st_mode):
        raise SubagentLayoutError(
            f"{printable(str(manifest_path))} is not a regular file; refusing to use it."
        )


def valid_subagent_relpath(line: str) -> bool:
    """Regex-free validation for an owned subagent project-relative POSIX path."""
    if not line or len(line) > MAX_RELPATH_LEN:
        return False
    for harness in HARNESS_ORDER:
        hdir, ext = HARNESS_SPECS[harness]
        prefix = f"{hdir}/"
        if line.startswith(prefix) and line.endswith(ext):
            stem = line[len(prefix) : len(line) - len(ext)]
            return "/" not in stem and valid_name(stem)
    return False


def read_manifest(project: Path) -> "set[str]":
    """Return bobp-owned subagent relpaths; missing, hostile, or oversized -> empty set."""
    text = _read_regular_safe(project, f"agents/{MANIFEST_NAME}", MAX_MANIFEST_BYTES)
    if text is None:
        return set()
    return {
        line.strip()
        for line in text.splitlines()
        if valid_subagent_relpath(line.strip())
    }


def write_manifest(project: Path, relpaths: "set[str]") -> None:
    """Atomically write agents/.bobp-subagents without following symlinks."""
    _check_dir_chain(project, ("agents",))
    agents_dir = project / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    valid = sorted(p for p in relpaths if valid_subagent_relpath(p))
    write_text_safely(agents_dir / MANIFEST_NAME, "".join(f"{p}\n" for p in valid))


def _unquote_yaml_scalar(raw: str) -> str:
    val = raw.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        if val[0] == '"':
            import json

            try:
                return str(json.loads(val))
            except ValueError:
                return val[1:-1]
        return val[1:-1].replace("''", "'")
    return val


def parse_persona_skill(text: str, expected_name: "str | None" = None) -> "tuple[str, str, str]":
    """Parse YAML frontmatter (`name`, `description`) and body via a linear line-by-line scan."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Persona SKILL.md missing opening '---' frontmatter fence.")
    end_idx: "int | None" = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError("Persona SKILL.md missing closing '---' frontmatter fence.")

    fields: dict[str, str] = {}
    for line in lines[1:end_idx]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, raw_val = line.split(":", 1)
        fields[key.strip()] = _unquote_yaml_scalar(raw_val)

    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not valid_name(name):
        raise ValueError(f"Invalid persona skill name: {name!r}")
    if expected_name is not None and name != expected_name:
        raise ValueError(f"Persona name {name!r} does not match directory {expected_name!r}")
    if not description:
        raise ValueError(f"Persona {name!r} has an empty description.")

    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n").rstrip() + "\n"
    return name, description, body


def _yaml_double_quote(text: str) -> str:
    """Render `text` as a single-line YAML double-quoted scalar with full control escaping."""
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif code < 0x20 or code == 0x7F or 0x80 <= code <= 0x9F or code in (0x2028, 0x2029):
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _toml_basic_string(text: str) -> str:
    """Render `text` as a single-line TOML basic string (escaping controls including 0x7F)."""
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\r":
            out.append("\\r")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _toml_multiline_string(text: str) -> str:
    """Render `text` as a TOML multiline basic string (`\"\"\"\\n...\\n\"\"\"`)."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    escaped_chars: list[str] = []
    for ch in normalized:
        code = ord(ch)
        if ch == "\\":
            escaped_chars.append("\\\\")
        elif ch in ("\n", "\t"):
            escaped_chars.append(ch)
        elif code < 0x20 or code == 0x7F:
            escaped_chars.append(f"\\u{code:04x}")
        else:
            escaped_chars.append(ch)
    escaped = "".join(escaped_chars)
    # Escape any run of 3+ quotes so it never terminates the multiline basic string.
    escaped = _TRIPLE_QUOTES_RE.sub(lambda m: '\\"' * len(m.group(0)), escaped)
    if not escaped.endswith("\n"):
        escaped += "\n"
    return f'"""\n{escaped}"""'


def _shared_memory_preamble(name: str) -> str:
    return (
        f"**Shared Working Memory:** Read and update `agents/{name}/state.md` and "
        "`agents/CHAT.md` at the project root (shared across Claude Code, Codex, "
        "and Gemini CLI — never store separate harness-local state)."
    )


def _generated_notice(name: str) -> str:
    return (
        f"Generated by bobp from .agents/skills/{name}/SKILL.md — "
        "overwritten by `bobp update`."
    )


def render_claude(name: str, description: str, body: str) -> str:
    """Render `.claude/agents/<name>.md`."""
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {_yaml_double_quote(description)}\n"
        "---\n"
        f"<!-- {_generated_notice(name)} -->\n\n"
        f"{_shared_memory_preamble(name)}\n\n"
        f"{body}"
    )


def render_gemini(name: str, description: str, body: str) -> str:
    """Render `.gemini/agents/<name>.md`."""
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {_yaml_double_quote(description)}\n"
        "kind: local\n"
        "---\n"
        f"<!-- {_generated_notice(name)} -->\n\n"
        f"{_shared_memory_preamble(name)}\n\n"
        f"{body}"
    )


def render_codex(name: str, description: str, body: str) -> str:
    """Render `.codex/agents/<name>.toml`."""
    instructions = f"{_shared_memory_preamble(name)}\n\n{body}"
    return (
        f"# {_generated_notice(name)}\n"
        f"name = {_toml_basic_string(name)}\n"
        f"description = {_toml_basic_string(description)}\n"
        f"developer_instructions = {_toml_multiline_string(instructions)}\n"
    )


_RENDERERS = {
    "claude": render_claude,
    "codex": render_codex,
    "gemini": render_gemini,
}


def compile_subagents(tmpl: Path) -> "dict[str, str]":
    """Compile all 10 packaged persona skills into `{rel_path: content}` across all 3 harnesses."""
    compiled: dict[str, str] = {}
    for name, src, is_persona in _skill_layout.template_skills(tmpl):
        if not is_persona:
            continue
        raw = src.read_text(encoding="utf-8")
        parsed_name, description, body = parse_persona_skill(raw, expected_name=name)
        for harness in HARNESS_ORDER:
            hdir, ext = HARNESS_SPECS[harness]
            rel = f"{hdir}/{parsed_name}{ext}"
            compiled[rel] = _RENDERERS[harness](parsed_name, description, body)
    return compiled


def place_subagents(project: Path, tmpl: Path, dry_run: bool = False) -> "list[Action]":
    """Install or refresh compiled subagent files for all 10 personas across 3 harnesses."""
    compiled = compile_subagents(tmpl)
    _preflight(project)
    owned = read_manifest(project)
    installed = set(owned)
    actions: list[Action] = []

    for rel in sorted(compiled):
        dest = project / rel
        try:
            st = os.lstat(dest)
        except FileNotFoundError:
            st = None
        except OSError as exc:
            actions.append(Action("skipped", rel, f"cannot inspect: {printable(str(exc))}"))
            continue

        if st is not None:
            if stat.S_ISLNK(st.st_mode):
                actions.append(Action("skipped", rel, "symlink; refusing to overwrite"))
                continue
            if not stat.S_ISREG(st.st_mode):
                actions.append(Action("skipped", rel, "not a regular file"))
                continue
            if rel not in owned:
                actions.append(Action("skipped", rel, "exists and was not installed by bobp"))
                continue
            kind = "replace"
        else:
            kind = "create"

        actions.append(Action(kind, rel, ""))
        installed.add(rel)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            write_text_safely(dest, compiled[rel])

    if not dry_run and (project / "agents").is_dir():
        write_manifest(project, installed)
    return actions


def gitignore_hides_subagents(project: Path) -> "list[str]":
    """Return harness subagent dirs (e.g. `.claude/agents/`) hidden by `<project>/.gitignore`."""
    text = _read_regular_safe(project, ".gitignore", MAX_GITIGNORE_BYTES)
    if text is None:
        return []
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    hidden: list[str] = []
    for harness in HARNESS_ORDER:
        hdir, _ = HARNESS_SPECS[harness]
        top = hdir.split("/")[0]  # e.g. ".claude"
        wholesale = {top, f"{top}/", f"/{top}", f"/{top}/"}
        wildcard = {f"{top}/*", f"/{top}/*", f"{top}/**", f"/{top}/**"}
        negations = {f"!{hdir}", f"!{hdir}/", f"!/{hdir}", f"!/{hdir}/"}

        if any(line in wholesale for line in lines):
            hidden.append(f"{hdir}/")
            continue
        is_hidden = False
        for line in lines:
            if line in wildcard:
                is_hidden = True
            elif line in negations:
                is_hidden = False
        if is_hidden:
            hidden.append(f"{hdir}/")
    return hidden


def diff_subagents(project: Path, tmpl: Path) -> "list[str]":
    """Compare bobp-owned subagent files in `project` against freshly compiled templates."""
    lines: list[str] = []
    if not _dir_chain_is_safe(project, ("agents",)):
        lines.append("Skipped subagent diff: agents/ is a symlink or not a directory.")
        return lines

    manifest_path = project / "agents" / MANIFEST_NAME
    try:
        st = os.lstat(manifest_path)
    except FileNotFoundError:
        lines.append(
            f"Note: agents/{MANIFEST_NAME} missing (pre-Sprint 5 install); "
            f"run `bobp update {printable(str(project))}` to generate harness subagents."
        )
        return lines
    except OSError:
        lines.append(f"Skipped subagent diff: cannot inspect agents/{MANIFEST_NAME}.")
        return lines

    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        lines.append(f"Skipped subagent diff: agents/{MANIFEST_NAME} is not a regular file.")
        return lines

    owned = read_manifest(project)
    compiled = compile_subagents(tmpl)
    for rel in sorted(compiled):
        if rel not in owned:
            continue
        target_text = _read_regular_safe(project, rel, MAX_SUBAGENT_BYTES)
        if target_text is None:
            lines.append(f"Only in template: {printable(rel)}")
        elif target_text != compiled[rel]:
            lines.append(f"Files differ: {printable(rel)}")
    return lines


def pull_subagents(src: Path, dest: Path, *, dry_run: bool = False) -> "list[Path]":
    """Safely pull existing bobp-owned subagent files from `src` into `dest`."""
    updated: list[Path] = []
    if not _dir_chain_is_safe(dest, ("agents",)):
        return updated
    owned = read_manifest(dest)
    for rel in sorted(owned):
        src_text = _read_regular_safe(src, rel, MAX_SUBAGENT_BYTES)
        if src_text is None:
            continue
        dest_text = _read_regular_safe(dest, rel, MAX_SUBAGENT_BYTES)
        if dest_text is None:
            continue
        dest_path = dest / rel
        if not dry_run:
            write_text_safely(dest_path, src_text)
        updated.append(dest_path)
    return updated


def summarize(actions: "list[Action]", *, dry_run: bool = False) -> "list[str]":
    """Concise per-harness summary; lists every skipped item and (in dry-run) every planned path."""
    lines: list[str] = []
    for harness in HARNESS_ORDER:
        hdir, _ = HARNESS_SPECS[harness]
        prefix = f"{hdir}/"
        bucket = [a for a in actions if a.path.startswith(prefix)]
        counts = {"create": 0, "replace": 0, "skipped": 0}
        for action in bucket:
            counts[action.kind] += 1
        lines.append(
            f"Subagents in {hdir}/: {counts['create']} added, "
            f"{counts['replace']} refreshed, {counts['skipped']} skipped."
        )
        if dry_run:
            for action in bucket:
                if action.kind == "create":
                    lines.append(f"  would create {printable(action.path)}")
                elif action.kind == "replace":
                    lines.append(f"  would refresh {printable(action.path)}")
                elif action.kind == "skipped":
                    lines.append(
                        f"  skipped {printable(action.path)}: {printable(action.note)}"
                    )
        else:
            for action in bucket:
                if action.kind == "skipped":
                    lines.append(
                        f"  skipped {printable(action.path)}: {printable(action.note)}"
                    )
    return lines
