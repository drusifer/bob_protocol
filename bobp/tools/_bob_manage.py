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
    live skills before install); _restore_skill_extensions() renames them
    back to SKILL.md in the target.
"""

import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

from ._common import find_project_root


def templates_dir() -> Path:
    import bobp

    return Path(bobp.__file__).parent / "templates"


def _require_dir(path: Path, label: str) -> None:
    if not path.is_dir():
        print(f"Error: {label} {path} does not exist", file=sys.stderr)
        sys.exit(1)


def _restore_skill_extensions(agents_dir: Path) -> None:
    for txt in agents_dir.rglob("SKILL.md.txt"):
        txt.rename(txt.with_suffix(""))


def _write_missing_state_files(agents_dir: Path, template_state: Path) -> None:
    for docs_dir in agents_dir.glob("*.docs"):
        state_file = docs_dir / "state.md"
        if not state_file.exists():
            shutil.copy2(template_state, state_file)


def _ensure_chat_md(agents_dir: Path, template_chat: Path) -> None:
    chat_file = agents_dir / "CHAT.md"
    if not chat_file.exists():
        shutil.copy2(template_chat, chat_file)


def _regen_chat_diagram(agents_dir: Path) -> None:
    from . import chat_diagram

    chat_diagram.regenerate(agents_dir / "CHAT.md", agents_dir / "CHAT.diagram.md")


def _run_setup_agent_links(target: Path) -> None:
    subprocess.run([sys.executable, "-m", "bobp.tools.setup_agent_links"], cwd=target)


def _merge_existing(src: Path, dst: Path) -> None:
    """Like `rsync -a --existing`: update files already present at dst, never create new ones."""
    if not src.is_dir():
        return
    for item in src.rglob("*"):
        if item.is_file():
            target = dst / item.relative_to(src)
            if target.exists():
                shutil.copy2(item, target)


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
    shutil.copytree(tmpl / "agents", target / "agents", dirs_exist_ok=True)
    _restore_skill_extensions(target / "agents")
    print("Setting up Claude skill links...")
    _run_setup_agent_links(target)
    print(f"\nDone. BobProtocol installed in {target}")
    print("Run `bobp tldr` inside it to verify.")


def update(target: Path) -> None:
    _require_dir(target, "target")
    tmpl = templates_dir()
    agents_dir = target / "agents"
    print(f"Updating BobProtocol in {target}...")
    shutil.copytree(tmpl / "agents" / "skills", agents_dir / "skills", dirs_exist_ok=True)
    shutil.copytree(tmpl / "agents" / "templates", agents_dir / "templates", dirs_exist_ok=True)
    for skill_txt in (tmpl / "agents").glob("*.docs/SKILL.md.txt"):
        docs_dir = agents_dir / skill_txt.parent.name
        docs_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_txt, docs_dir / "SKILL.md")
    _restore_skill_extensions(agents_dir)

    print("Ensuring agent state files are initialised...")
    _write_missing_state_files(agents_dir, tmpl / "agents" / "templates" / "_template_state.md")
    _ensure_chat_md(agents_dir, tmpl / "agents" / "templates" / "_template_CHAT.md")
    _regen_chat_diagram(agents_dir)

    print("Updating Claude skill links...")
    _run_setup_agent_links(target)
    print(f"\nDone. BobProtocol updated in {target}")


def pull(src: Path) -> None:
    _require_dir(src, "source")
    root = find_project_root()
    agents_dir = root / "agents"
    print(f"Pulling BobProtocol updates from {src}...")
    _merge_existing(src / "agents" / "skills", agents_dir / "skills")
    _merge_existing(src / "agents" / "templates", agents_dir / "templates")
    for docs_dir in agents_dir.glob("*.docs"):
        src_skill = src / "agents" / docs_dir.name / "SKILL.md"
        if src_skill.exists():
            shutil.copy2(src_skill, docs_dir / "SKILL.md")
    print(f"\nDone. BobProtocol pulled from {src}")


def clean() -> None:
    root = find_project_root()
    agents_dir = root / "agents"
    print("Removing generated symlinks...")
    subprocess.run(
        [sys.executable, "-m", "bobp.tools.teardown_agent_links", "--keep-mcp"], cwd=root
    )
    print("Resetting agent state files to templates...")
    template_state = agents_dir / "templates" / "_template_state.md"
    for docs_dir in agents_dir.glob("*.docs"):
        shutil.copy2(template_state, docs_dir / "state.md")
    shutil.copy2(agents_dir / "templates" / "_template_CHAT.md", agents_dir / "CHAT.md")
    _regen_chat_diagram(agents_dir)
    print("Done. Environment cleaned and state reset.")


def diff(target: Path) -> None:
    _require_dir(target, "target")
    tmpl = templates_dir()
    print(f"Diffing BobProtocol template vs {target}")
    print()
    for name in ("skills", "templates"):
        src_dir = tmpl / "agents" / name
        dst_dir = target / "agents" / name
        if dst_dir.is_dir():
            _diff_trees(src_dir, dst_dir)
        else:
            print(f"Only in template: agents/{name}/")
    for skill_txt in (tmpl / "agents").glob("*.docs/SKILL.md.txt"):
        docs_name = skill_txt.parent.name
        tgt_file = target / "agents" / docs_name / "SKILL.md"
        if tgt_file.is_file():
            if skill_txt.read_bytes() != tgt_file.read_bytes():
                print(f"Files differ: agents/{docs_name}/SKILL.md")
        else:
            print(f"Only in template: agents/{docs_name}/SKILL.md")
    print("\nDone.")
