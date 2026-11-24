#!/usr/bin/env python3
"""
Project setup — via MCP, project capabilities and .gitignore; creates no links.

TLDR:
    Skills and personas are real directories in .agents/skills/ (placed by
    `bobp install`/`bobp update`, see _skill_layout) and the shared instructions
    are a real root AGENTS.md, so there is nothing left to link. What remains:
    converts older projects whose persona folders are agents/<name>.docs/ to
    the current agents/<name>/ layout (migrate_legacy_layout(), the only place
    that knows that layout); removes the tool scripts older projects carried in
    agents/tools/ now that they ship inside bobp (remove_legacy_tools(), leaving
    project-specific tools and trace_rules.json alone); install_via_mcp() writes
    generic via MCP config; install_codex_via_mcp() registers the same server
    with Codex using `codex mcp add`; setup_project_capabilities() writes
    agents/PROJECT.md when absent; ensure_gitignore_entries() idempotently adds
    .mcp.json and .via/ to .gitignore (both are machine-local and must never be
    committed). find_persona_dirs() discovers persona folders (agents/<name>/
    holding state.md).
    Role in the system: run from the project root by install/update and by hand.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from ._common import find_persona_dirs, find_project_root
except ImportError:
    from _common import find_persona_dirs, find_project_root


# The pre-agents/<name>/ layout. Nothing outside this module knows about it.
LEGACY_PERSONA_SUFFIX = ".docs"
# Generic stand-ins the docs use for "any persona", e.g. agents/[persona].docs/
LEGACY_REF_PLACEHOLDERS = ("[persona]", "<persona>", "<name>", "<agent>", "agent", "*")
# Chat logs are history, not instructions — leave the paths they mention alone.
REWRITE_SKIP_NAMES = {"CHAT.md", "CHAT.diagram.md"}
REWRITE_SKIP_DIRS = {"chat_archive"}
REWRITE_SUFFIXES = {".md", ".txt", ".template"}




def migrate_persona_folders(agents_dir: Path) -> list[str]:
    """Rename legacy agents/<name>.docs/ folders to agents/<name>/.

    If agents/<name>/ already exists the legacy folder's files are moved into
    it without overwriting anything; a legacy folder left with conflicting
    files is kept and reported. Returns the persona names that were migrated.
    """
    migrated = []

    for legacy in sorted(agents_dir.glob(f"*{LEGACY_PERSONA_SUFFIX}")):
        if not legacy.is_dir() or legacy.is_symlink():
            continue
        name = legacy.name.removesuffix(LEGACY_PERSONA_SUFFIX)
        if not name:
            continue
        target = agents_dir / name

        if not target.exists():
            legacy.rename(target)
            print(f"  ✅ agents/{legacy.name}/ -> agents/{name}/")
            migrated.append(name)
            continue

        if not target.is_dir():
            print(f"  ⚠️  Skipping agents/{legacy.name}/ - agents/{name} exists and is not a directory")
            continue

        conflicts = 0
        for item in sorted(legacy.rglob("*")):
            if item.is_dir():
                continue
            dest = target / item.relative_to(legacy)
            if dest.exists():
                conflicts += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            item.rename(dest)
        if conflicts:
            print(
                f"  ⚠️  agents/{legacy.name}/ kept - {conflicts} file(s) already exist in "
                f"agents/{name}/; merge them by hand"
            )
        else:
            shutil.rmtree(legacy)
            print(f"  ✅ agents/{legacy.name}/ merged into agents/{name}/")
        migrated.append(name)

    return migrated


def rewrite_legacy_refs(agents_dir: Path, persona_names: list[str]) -> int:
    """Rewrite `<name>.docs` path references in agent docs to `<name>`.

    Only the given persona names and the generic placeholders are rewritten, so
    unrelated text that happens to end in .docs is left alone. Returns the
    number of files changed.
    """
    tokens = "|".join(re.escape(t) for t in (*persona_names, *LEGACY_REF_PLACEHOLDERS))
    # "their `.docs/` folder" style prose has no name in front of the suffix.
    pattern = re.compile(rf"(?<![\w.-])({tokens})\.docs\b|(?<=`)\.docs/(?=`)")

    def replace(match: re.Match) -> str:
        return match.group(1) if match.group(1) else "<name>/"

    changed = 0
    for path in sorted(agents_dir.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix not in REWRITE_SUFFIXES:
            continue
        if path.name in REWRITE_SKIP_NAMES:
            continue
        if REWRITE_SKIP_DIRS & set(path.relative_to(agents_dir).parts[:-1]):
            continue
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        new_text = pattern.sub(replace, text)
        if new_text != text:
            path.write_text(new_text)
            changed += 1

    return changed


def migrate_legacy_layout(agents_dir: Path) -> list[str]:
    """Convert an older agents/<name>.docs/ project to agents/<name>/ in place.

    A no-op (and silent) on a project already on the current layout. Returns
    the persona names that were migrated.
    """
    if not any(agents_dir.glob(f"*{LEGACY_PERSONA_SUFFIX}")):
        return []

    print("\n📁 Converting persona folders to agents/<name>/...")
    migrated = migrate_persona_folders(agents_dir)
    if migrated:
        names = sorted({name for name, _ in find_persona_dirs(agents_dir)} | set(migrated))
        rewritten = rewrite_legacy_refs(agents_dir, names)
        if rewritten:
            print(f"  ✅ Updated persona folder references in {rewritten} file(s)")
    return migrated


# Scripts that used to be copied into <project>/agents/tools/ and are now bobp
# subcommands. A project copy is never what `bobp <subcommand>` runs, so it can
# only go stale. Anything else in agents/tools/ — a project's own bespoke tools,
# or trace_rules.json, which `bobp trace-annotate` still reads from there — is
# not ours to remove.
LEGACY_TOOL_SCRIPTS = {
    "chat.py": "bobp chat",
    "chat_merge.py": "bobp chat-merge",
    "mkf.py": "bobp make",
    "prep_tldr.py": "bobp prep-tldr",
    "session_trace.py": "bobp session-trace",
    "setup_agent_links.py": "bobp setup-agent-links",
    "teardown_agent_links.py": "bobp teardown-agent-links",
    "tldr.py": "bobp tldr",
    "trace_annotate.py": "bobp trace-annotate",
}


def remove_legacy_tools(agents_dir: Path) -> list[str]:
    """Delete the superseded tool scripts from agents/tools/.

    Only the file names in LEGACY_TOOL_SCRIPTS are removed. The directory's
    __pycache__ goes with them, and the directory itself is removed if that
    leaves it empty. A no-op (and silent) when there is nothing to remove.
    Returns the names of the scripts removed.
    """
    tools_dir = agents_dir / "tools"
    if not tools_dir.is_dir() or tools_dir.is_symlink():
        return []

    present = [name for name in sorted(LEGACY_TOOL_SCRIPTS)
               if (tools_dir / name).is_file() or (tools_dir / name).is_symlink()]
    if not present:
        return []

    print("\n🧹 Removing tool scripts that now ship inside bobp...")
    removed = []
    for name in present:
        try:
            (tools_dir / name).unlink()
        except OSError as exc:
            print(f"  ⚠️  Could not remove agents/tools/{name}: {exc}")
            continue
        removed.append(name)
        print(f"  ✅ agents/tools/{name} removed - use `{LEGACY_TOOL_SCRIPTS[name]}`")

    shutil.rmtree(tools_dir / "__pycache__", ignore_errors=True)
    remaining = sorted(item.name for item in tools_dir.iterdir())
    if not remaining:
        tools_dir.rmdir()
        print("  ✅ agents/tools/ removed (empty)")
    else:
        print(f"  ℹ️  agents/tools/ kept: {', '.join(remaining)}")
    return removed


def get_codex_home() -> Path:
    """Return Codex home, honoring CODEX_HOME when set."""
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def install_via_mcp(project_root: Path) -> bool:
    """Delegate MCP setup to via's installer."""
    print("\n📡 Installing via MCP integration...")

    if not shutil.which("via"):
        print("  ⚠️  via not found on PATH — skipping MCP setup")
        print("     Install via and re-run: pip install via")
        return False

    import subprocess
    result = subprocess.run(
        ["via", "install", "mcp"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ❌ via install mcp failed: {result.stderr.strip()}")
        return False

    print(f"  ✅ via install mcp ({result.stdout.strip() or 'done'})")
    return configure_project_via_mcp(project_root)


def configure_project_via_mcp(project_root: Path) -> bool:
    """Harden project .mcp.json so via MCP works in sandboxed clients."""
    mcp_json = project_root / ".mcp.json"
    try:
        data = json.loads(mcp_json.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  ⚠️  Could not read {mcp_json}: {exc}")
        return False

    via_entry = data.setdefault("mcpServers", {}).setdefault("via", {})
    args = list(via_entry.get("args", []))
    if "serve" in args and "--no-web" not in args:
        serve_index = args.index("serve")
        args.insert(serve_index + 1, "--no-web")
    via_entry["args"] = args

    env = dict(via_entry.get("env", {}))
    env["HOME"] = str(project_root)
    via_entry["env"] = env

    try:
        mcp_json.write_text(json.dumps(data, indent=2) + "\n")
    except OSError as exc:
        print(f"  ⚠️  Could not update {mcp_json}: {exc}")
        return False

    print("  ✅ Hardened .mcp.json for sandboxed via MCP startup")
    return True


def ensure_via_index(project_root: Path) -> bool:
    """Create the via index required by the MCP server when it is missing."""
    print("\n📇 Checking via index...")

    index_db = project_root / ".via" / "index.db"
    if index_db.exists():
        print("  ℹ️  via index already exists")
        return True

    via_bin = shutil.which("via")
    if not via_bin:
        print("  ⚠️  via not found on PATH — cannot create via index")
        return False

    result = subprocess.run(
        [via_bin, "index", str(project_root)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ❌ via index failed: {result.stderr.strip()}")
        return False

    print(f"  ✅ via index ({result.stdout.strip() or 'done'})")
    return True


def install_codex_via_mcp(project_root: Path) -> bool:
    """Register the via MCP stdio server with Codex."""
    print("\n📡 Installing Codex via MCP integration...")

    codex_bin = shutil.which("codex")
    if not codex_bin:
        print("  ⚠️  codex not found on PATH — skipping Codex MCP setup")
        return False

    via_bin = shutil.which("via")
    if not via_bin:
        print("  ⚠️  via not found on PATH — skipping Codex MCP setup")
        print("     Install via and re-run: pip install via")
        return False

    expected_args = ["mcp", "serve", "--no-web", str(project_root)]
    expected_env = f"HOME={project_root}"

    def add_server() -> bool:
        result = subprocess.run(
            [
                codex_bin,
                "mcp",
                "add",
                "via",
                "--env",
                expected_env,
                "--",
                via_bin,
                *expected_args,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ❌ codex mcp add via failed: {result.stderr.strip()}")
            print("     Manual fallback:")
            print(f"     codex mcp add via --env {expected_env} -- {via_bin} {' '.join(expected_args)}")
            return False

        print(f"  ✅ codex mcp add via ({result.stdout.strip() or 'done'})")
        return True

    existing = subprocess.run(
        [codex_bin, "mcp", "get", "via"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if existing.returncode != 0:
        return add_server()

    existing_config = existing.stdout
    if (
        f"command: {via_bin}" in existing_config
        and f"args: {' '.join(expected_args)}" in existing_config
        and expected_env in existing_config
    ):
        print("  ℹ️  Codex MCP server 'via' already points at this project")
        return True

    print("  ℹ️  Replacing existing Codex MCP server 'via' with this project")
    remove = subprocess.run(
        [
            codex_bin,
            "mcp",
            "remove",
            "via",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if remove.returncode != 0:
        print(f"  ❌ codex mcp remove via failed: {remove.stderr.strip()}")
        return False

    return add_server()


def setup_project_capabilities(project_root: Path, via_enabled: bool) -> bool:
    """Create agents/PROJECT.md if missing so personas know available tools."""
    project_file = project_root / "agents" / "PROJECT.md"
    print("\n📁 Setting up project capability declarations...")

    if project_file.exists():
        print("  ℹ️  agents/PROJECT.md already exists; leaving it unchanged")
        return False

    via_state = "enabled" if via_enabled else "disabled"
    content = f"""---
# PROJECT.md — Project Capability Declarations
#
# Generated by `bobp setup-agent-links`.
# All personas read this file on cold start to adapt their workflow to available tools.
---

# Project: {project_root.name}

## Description
BobProtocol-enabled project.

## Capabilities

### via
```
via: {via_state}
```
- When `enabled`: all personas use `via` for code navigation before falling back to Grep/Glob/Read.
- When `disabled`: personas use standard file and shell tools.

## Project Standards
Follow the repository instructions in `AGENTS.md` and persona state files.

## Key Artifacts
- `agents/CHAT.md` — Team communication log
- `AGENTS.md` — Shared agent instructions (project root)
- `.agents/skills/` — Persona and shared skills
- `agents/<name>/` — Persona state and instructions

## Notes
Update this file when project capabilities change.
"""

    try:
        project_file.write_text(content)
    except OSError as exc:
        print(f"  ⚠️  Could not create {project_file}: {exc}")
        return False

    print(f"  ✅ Created agents/PROJECT.md with via: {via_state}")
    return True


GITIGNORE_ENTRIES = {
    ".mcp.json": "Bob Protocol / via — machine-local MCP config (absolute paths), not portable",
    ".via/": "Bob Protocol / via — local index database, not portable",
}


def ensure_gitignore_entries(project_root: Path) -> bool:
    """Ensures .mcp.json and .via/ are gitignored — both are machine-local
    (an absolute-path MCP config and a local index db) and should never be
    committed. Idempotent: safe to run on a project that already has them.
    """
    gitignore_path = project_root / ".gitignore"
    existing = gitignore_path.read_text() if gitignore_path.exists() else ""
    existing_lines = set(existing.splitlines())

    missing = [entry for entry in GITIGNORE_ENTRIES if entry not in existing_lines]
    if not missing:
        return False

    lines = ["", "# Bob Protocol / via — machine-local config and index, not portable"]
    for entry in missing:
        lines.append(entry)
    addition = "\n".join(lines) + "\n"

    with open(gitignore_path, "a") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(addition)

    print(f"  ✅ Added {', '.join(missing)} to .gitignore")
    return True


def main():
    print("🔧 Agent Discovery Links Setup")
    print("=" * 40)

    # Find project root
    project_root = find_project_root()
    agents_dir = project_root / "agents"
    print(f"\nProject root: {project_root}")
    print(f"Agents dir: {agents_dir}")

    # Convert an older agents/<name>.docs/ project before discovering personas
    migrate_legacy_layout(agents_dir)

    # Drop the agents/tools/*.py copies that bobp subcommands replaced
    remove_legacy_tools(agents_dir)

    # Find persona folders
    personas = find_persona_dirs(agents_dir)
    if not personas:
        print("\n❌ No persona folders found!")
        print("   Expected: agents/<name>/state.md")
        sys.exit(1)

    print(f"\nFound {len(personas)} personas:")
    for name, _ in personas:
        print(f"  • {name}")

    # Delegate generic MCP setup to via, then register the server with Codex.
    via_index_ok = ensure_via_index(project_root)
    via_ok = install_via_mcp(project_root)
    codex_via_ok = install_codex_via_mcp(project_root)
    project_md_ok = setup_project_capabilities(project_root, via_index_ok and (via_ok or codex_via_ok))

    print("\n📄 Checking .gitignore for machine-local files...")
    ensure_gitignore_entries(project_root)

    print("\n✅ Done. No links were created.")
    print("\nSkills are real directories in .agents/skills/ (Codex, Gemini CLI, Cursor, Copilot);")
    print("the shared instructions are AGENTS.md at the project root.")
    print("Claude Code does not read .agents/skills/; Gemini CLI also needs")
    print('context.fileName to include "AGENTS.md" in its own settings.')
    if via_index_ok:
        print("  • via index (.via/index.db)")
    if via_ok:
        print("  • via MCP server (via install mcp)")
    if codex_via_ok:
        print(f"  • Codex via MCP server ({get_codex_home() / 'config.toml'})")
    if project_md_ok:
        print("  • Project capabilities (agents/PROJECT.md)")


if __name__ == "__main__":
    main()
