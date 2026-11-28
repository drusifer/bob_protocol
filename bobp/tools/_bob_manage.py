"""Shared implementation for the bob-protocol project-management subcommands.

TLDR:
    Python port of the old install_bob/update_bob/pull_bob/clean_bob/diff_bob
    Makefile targets (which used rsync + shell loops). install()/update()/
    pull()/clean()/diff() are called by the thin bob_install.py/bob_update.py/
    bob_pull.py/bob_clean.py/bob_diff.py argparse wrappers that bobp.cli
    dispatches to.

    Source of truth for install/update/diff is the packaged template dir
    (bobp/templates, found via `import bobp`), not a sibling agents/ — that
    distinction is what keeps a project's own real CHAT.md/state.md/lessons.md
    from ever being shipped as if they were generic template content.
    Template SKILL.md files ship as SKILL.md.txt (so they aren't picked up as
    live skills before install); _skill_layout.place_skills() copies them into
    the target's .agents/skills/<name>/SKILL.md as real files. Persona memory
    (state.md, ...) is copied to agents/<persona>/ and stays there.
"""

import filecmp
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import _path_rewrite, _skill_layout, _subagent_layout, setup_agent_links
from ._common import STAMP_NAME, find_persona_dirs, find_project_root, write_text_safely


def write_stamp(agents_dir: Path) -> None:
    """Record which bobp version set up (or last updated) this project."""
    import bobp

    write_text_safely(agents_dir / STAMP_NAME, f"{bobp.__version__}\n")


def templates_dir() -> Path:
    import bobp

    return Path(bobp.__file__).parent / "templates"


def _require_dir(path: Path, label: str) -> None:
    if not path.is_dir():
        print(f"Error: {label} {path} does not exist", file=sys.stderr)
        sys.exit(1)


def _ignore_skill_sources(tmpl_agents: Path):
    """copytree ignore function: skills are placed by _skill_layout, not copied into agents/."""

    def ignore(directory: str, names: "list[str]") -> "set[str]":
        here = Path(directory)
        skipped = {name for name in names if name == "SKILL.md.txt"}
        if here == tmpl_agents:
            # Skills are placed by _skill_layout; AGENTS.md goes to the project root.
            skipped.update({"skills", "AGENTS.md", "AGENT.md"} & set(names))
        elif here.parent == tmpl_agents:
            skipped.update(name for name in names if name in ("evals", "references"))
        return skipped

    return ignore


def _print_lines(lines: "list[str]") -> None:
    for line in lines:
        print(line)


def _report(actions: "list[_skill_layout.Action]") -> None:
    _print_lines(_skill_layout.summarize(actions))


def _place_subagents_or_exit(
    target: Path, tmpl: Path, *, dry_run: bool = False
) -> "list[_skill_layout.Action]":
    try:
        return _subagent_layout.place_subagents(target, tmpl, dry_run=dry_run)
    except _subagent_layout.SubagentLayoutError as exc:
        print(f"Error: {_skill_layout.printable(str(exc))}", file=sys.stderr)
        sys.exit(1)


def _warn_hidden_subagents(target: Path) -> None:
    hidden = _subagent_layout.gitignore_hides_subagents(target)
    if hidden:
        joined = ", ".join(_skill_layout.printable(d) for d in hidden)
        print(
            f"Note: .gitignore hides generated subagent directory(ies) ({joined}) from Git. "
            "Use an allowlist (e.g. `.claude/*` + `!.claude/agents/`) if you want to commit them."
        )


def _codex_home() -> Path:
    import os

    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


_TEMPLATE_CHECK_RE = re.compile(
    r"(?ms)^<!-- RUBRIC-START -->\s*\n.*?^<!-- RUBRIC-END -->\s*\n?"
)


def _copy_artifact_template(template: Path, destination: Path) -> None:
    """Copy an artifact template without its reviewer-only check block."""
    shutil.copy2(template, destination)
    content = _TEMPLATE_CHECK_RE.sub("", destination.read_text()).rstrip() + "\n"
    destination.write_text(content)


def _write_missing_state_files(
    agents_dir: Path, template_state: Path, persona_names: "tuple[str, ...]" = ()
) -> None:
    """Give every persona a state.md; `persona_names` are personas that must exist even if new."""
    for name in persona_names:
        (agents_dir / name).mkdir(parents=True, exist_ok=True)
    persona_dirs = dict(find_persona_dirs(agents_dir))
    persona_dirs.update({name: agents_dir / name for name in persona_names})
    for persona_dir in persona_dirs.values():
        state_file = persona_dir / "state.md"
        if not state_file.exists():
            _copy_artifact_template(template_state, state_file)


def _ensure_chat_md(agents_dir: Path, template_chat: Path) -> None:
    chat_file = agents_dir / "CHAT.md"
    if not chat_file.exists():
        _copy_artifact_template(template_chat, chat_file)


def _regen_chat_diagram(agents_dir: Path) -> None:
    from . import chat_diagram

    chat_diagram.regenerate(agents_dir / "CHAT.md", agents_dir / "CHAT.diagram.md")


def _run_setup_agent_links(target: Path) -> None:
    subprocess.run([sys.executable, "-m", "bobp.tools.setup_agent_links"], cwd=target)


def _merge_existing(src: Path, dst: Path, *, dry_run: bool = False) -> "list[Path]":
    """Like `rsync -a --existing`: update files already present at dst, never create new ones."""
    updated: list[Path] = []
    if not src.is_dir():
        return updated
    for item in sorted(src.rglob("*")):
        if item.is_file():
            target = dst / item.relative_to(src)
            if target.exists():
                if not dry_run:
                    shutil.copy2(item, target)
                updated.append(target)
    return updated


def _diff_trees(a: Path, b: Path) -> None:
    cmp = filecmp.dircmp(a, b)
    for name in sorted(cmp.diff_files):
        print(f"Files {a / name} and {b / name} differ")
    for name in sorted(cmp.left_only):
        print(f"Only in {a}: {name}")
    for name in sorted(cmp.right_only):
        print(f"Only in {b}: {name}")
    for name, sub in cmp.subdirs.items():
        _diff_trees(a / name, b / name)


def install(target: Path, force: bool = False) -> None:
    _require_dir(target, "target")
    if (target / "agents").exists() and not force:
        print(
            f"Error: {target}/agents already exists. "
            "Use `bobp update` to refresh an existing install, or pass --force to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    tmpl = templates_dir()
    print(f"Installing BobProtocol into {target}...")
    shutil.copytree(
        tmpl / "agents",
        target / "agents",
        dirs_exist_ok=True,
        ignore=_ignore_skill_sources(tmpl / "agents"),
    )
    print("Installing skills into .agents/skills/...")
    _report(_skill_layout.place_skills(target, tmpl))
    print("Generating harness subagent definitions (.claude, .codex, .gemini)...")
    _print_lines(_subagent_layout.summarize(_place_subagents_or_exit(target, tmpl)))
    _warn_hidden_subagents(target)
    _print_lines(_skill_layout.describe(_skill_layout.ensure_root_agents_md(target, tmpl)))
    _run_setup_agent_links(target)
    write_stamp(target / "agents")
    print(f"\nDone. BobProtocol installed in {target}")
    print("Run `bobp tldr` inside it to verify.")


def update(target: Path, *, dry_run: bool = False) -> None:
    _require_dir(target, "target")
    tmpl = templates_dir()
    agents_dir = target / "agents"
    if dry_run:
        print(f"Dry-run: previewing BobProtocol update in {target} (no changes will be written)...")
        cleanup = _skill_layout.remove_legacy_links(target, dry_run=True)
        cleanup += _skill_layout.migrate_legacy(target, tmpl, dry_run=True)
        if cleanup:
            print("Would migrate from older layout:")
            _print_lines(_skill_layout.describe(cleanup))
        # If `.agents` is a verified legacy bobp symlink slated for removal above,
        # preview skill creation directly without calling place_skills() through the unremoved link.
        removing_legacy_agents_link = any(
            a.kind == "remove" and a.path == ".agents" for a in cleanup
        )
        if removing_legacy_agents_link:
            skill_actions = [
                _skill_layout.Action(
                    "create",
                    f"{_skill_layout.SKILLS_DIR.as_posix()}/{name}",
                    "new skill (after removing legacy .agents link)",
                )
                for name, _, _ in _skill_layout.template_skills(tmpl)
            ]
        else:
            skill_actions = _skill_layout.place_skills(target, tmpl, dry_run=True)
        _report(skill_actions)
        subagent_actions = _place_subagents_or_exit(target, tmpl, dry_run=True)
        _print_lines(_subagent_layout.summarize(subagent_actions, dry_run=True))
        _warn_hidden_subagents(target)
        _print_lines(_skill_layout.describe(_skill_layout.ensure_root_agents_md(target, tmpl, dry_run=True)))
        owned = _skill_layout.read_manifest(agents_dir) if agents_dir.is_dir() else set()
        _print_lines(
            _skill_layout.describe(
                _skill_layout.remove_claude_skill_copies(target, owned, dry_run=True)
            )
        )
        print("Would refresh agents/templates/, ensure missing persona state.md/CHAT.md, and update version stamp.")
        print("Dry-run complete. No files were modified.")
        return

    print(f"Updating BobProtocol in {target}...")
    if agents_dir.is_dir():
        # Convert an older-layout project first, so the refreshed persona files
        # below land in its existing (renamed) folders instead of beside them.
        setup_agent_links.migrate_legacy_layout(agents_dir)
    agents_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(tmpl / "agents" / "templates", agents_dir / "templates", dirs_exist_ok=True)

    # Older layouts first: drop bobp's own links, then move skills out of agents/.
    cleanup = _skill_layout.remove_legacy_links(target)
    cleanup += _skill_layout.migrate_legacy(target, tmpl)
    if cleanup:
        print("Migrating from the older layout...")
        _print_lines(_skill_layout.describe(cleanup))
    print("Updating skills in .agents/skills/...")
    _report(_skill_layout.place_skills(target, tmpl))
    print("Updating harness subagent definitions (.claude, .codex, .gemini)...")
    _print_lines(_subagent_layout.summarize(_place_subagents_or_exit(target, tmpl)))
    _warn_hidden_subagents(target)
    _print_lines(_skill_layout.describe(_skill_layout.ensure_root_agents_md(target, tmpl)))
    owned = _skill_layout.read_manifest(agents_dir)
    _print_lines(_skill_layout.describe(_skill_layout.remove_claude_skill_copies(target, owned)))
    personas = sorted(set(_path_rewrite.PERSONAS) | {name for name, _ in find_persona_dirs(agents_dir)})
    rewritten = _path_rewrite.rewrite_files(_path_rewrite.project_targets(target, owned), personas)
    if rewritten:
        print(f"Updated path references in {len(rewritten)} file(s) to the .agents/skills layout.")
    if _skill_layout.gitignore_hides_skills(target):
        print(
            "Note: .gitignore ignores the whole .agents/ directory, so the skills in "
            ".agents/skills/ will not be committed. Remove that ignore rule if you want to share them."
        )
    stale = _skill_layout.legacy_codex_links(target, _codex_home())
    if stale:
        print(
            f"Note: {len(stale)} skill link(s) from older bobp versions remain in "
            f"{_codex_home() / 'skills'}; `bobp teardown-agent-links` removes them."
        )

    print("Ensuring agent state files are initialised...")
    _write_missing_state_files(
        agents_dir,
        tmpl / "agents" / "templates" / "_template_state.md",
        tuple(_skill_layout.persona_names(tmpl)),
    )
    _ensure_chat_md(agents_dir, tmpl / "agents" / "templates" / "_template_CHAT.md")
    _regen_chat_diagram(agents_dir)

    _run_setup_agent_links(target)
    write_stamp(agents_dir)
    print(f"\nDone. BobProtocol updated in {target}")


def pull(src: Path, *, dry_run: bool = False) -> None:
    _require_dir(src, "source")
    root = find_project_root()
    agents_dir = root / "agents"
    if dry_run:
        print(f"Dry-run: previewing BobProtocol pull from {src} into {root}...")
    else:
        print(f"Pulling BobProtocol updates from {src}...")
    owned = _skill_layout.read_manifest(agents_dir)
    updated: list[Path] = []
    for name in sorted(owned):
        updated += _merge_existing(
            src / _skill_layout.SKILLS_DIR / name,
            root / _skill_layout.SKILLS_DIR / name,
            dry_run=dry_run,
        )
    updated += _merge_existing(src / "agents" / "templates", agents_dir / "templates", dry_run=dry_run)
    updated += _subagent_layout.pull_subagents(src, root, dry_run=dry_run)
    if dry_run:
        for path in updated:
            print(f"  would update {_skill_layout.printable(str(path.relative_to(root)))}")
        print(f"Dry-run complete: {len(updated)} file(s) would be updated. No files were modified.")
        return
    print(f"\nDone. BobProtocol pulled from {src}")


def clean(*, dry_run: bool = False, yes: bool = False) -> None:
    root = find_project_root()
    agents_dir = root / "agents"
    targets: list[Path] = [
        persona_dir / "state.md" for _, persona_dir in find_persona_dirs(agents_dir)
    ]
    targets.append(agents_dir / "CHAT.md")
    targets.append(agents_dir / "CHAT.diagram.md")

    if dry_run:
        print("Dry-run: the following files would be reset:")
        for path in targets:
            print(f"  would reset {_skill_layout.printable(str(path.relative_to(root)))}")
        print("Dry-run complete. No files were modified.")
        return

    if not yes:
        print("The following files would be reset:", file=sys.stderr)
        for path in targets:
            print(f"  {_skill_layout.printable(str(path.relative_to(root)))}", file=sys.stderr)
        print(
            "Refusing to reset persona state and CHAT.md without confirmation. "
            "Re-run with: bobp clean --yes",
            file=sys.stderr,
        )
        sys.exit(2)

    print("Removing generated symlinks...")
    subprocess.run(
        [sys.executable, "-m", "bobp.tools.teardown_agent_links", "--keep-mcp"], cwd=root
    )
    print("Resetting agent state files to templates...")
    template_state = agents_dir / "templates" / "_template_state.md"
    for _, persona_dir in find_persona_dirs(agents_dir):
        _copy_artifact_template(template_state, persona_dir / "state.md")
    _copy_artifact_template(
        agents_dir / "templates" / "_template_CHAT.md", agents_dir / "CHAT.md"
    )
    _regen_chat_diagram(agents_dir)
    print("Done. Environment cleaned and state reset.")


def diff(target: Path) -> None:
    _require_dir(target, "target")
    tmpl = templates_dir()
    print(f"Diffing BobProtocol template vs {target}")
    print()
    src_dir = tmpl / "agents" / "templates"
    dst_dir = target / "agents" / "templates"
    if dst_dir.is_dir():
        _diff_trees(src_dir, dst_dir)
    else:
        print("Only in template: agents/templates/")
    for name, source, is_persona in _skill_layout.template_skills(tmpl):
        template_file = source if is_persona else source / "SKILL.md.txt"
        rel = f"{_skill_layout.SKILLS_DIR.as_posix()}/{name}/SKILL.md"
        tgt_file = target / rel
        if tgt_file.is_file():
            if template_file.read_bytes() != tgt_file.read_bytes():
                print(f"Files differ: {rel}")
        else:
            print(f"Only in template: {rel}")
    _print_lines(_subagent_layout.diff_subagents(target, tmpl))
    print("\nDone.")
