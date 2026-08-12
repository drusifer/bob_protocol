#!/usr/bin/env python3
"""
bobp chat-report — archive agents/CHAT.md + CHAT.diagram.md under a sprint
moniker, and combine every archived sprint back into CHAT_FULL.md/.diagram.md.

TLDR:
    Two modes, both pure-Python I/O (the caller supplies only a moniker and a
    summary string; no file paths, no manual copying):
      archive  (default): reads CHAT.md/CHAT.diagram.md, writes
        agents/chat_archive/CHAT_<MONIKER>.md and .diagram.md headed by the
        supplied summary, then resets the live CHAT.md to a short pointer at
        the new archive (and regenerates the now-empty diagram). Pass --svg
        to also render the diagram to a standalone .svg (via mermaid_render/,
        a real Chrome + mermaid-cli) and embed that as a plain markdown image
        instead of a live ```mermaid fence — GitHub's embedded renderer has
        been observed to not handle some diagrams correctly (small/dense
        text, notes not wrapping) even when the source is valid Mermaid; a
        pre-rendered image sidesteps that entirely. Requires Node + a
        discoverable Chrome/Chromium; falls back to the mermaid fence with a
        warning (never a hard failure) if either is missing.
      combine  (--combine): concatenates every CHAT_<MONIKER>.md/.diagram.md
        already in agents/chat_archive/ into CHAT_FULL.md/.diagram.md, using
        each archive's own summary heading as a section header. Idempotent —
        safe to re-run after adding a new archive. Needs no --svg flag of its
        own: it concatenates each archive's .diagram.md verbatim, so any
        image-embedded archives (from `archive --svg`) carry their image
        reference straight through.
    Reuses parse_blocks()/BLOCK_SEP from chat_merge.py rather than
    reimplementing CHAT.md's header/blocks split.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from . import chat_diagram
    from ._common import find_project_root
    from .chat_merge import BLOCK_SEP, parse_blocks
except ImportError:
    import chat_diagram
    from _common import find_project_root
    from chat_merge import BLOCK_SEP, parse_blocks

MERMAID_RENDER_DIR = Path(__file__).resolve().parent / "mermaid_render"

ARCHIVE_DIRNAME = "chat_archive"
FENCE_MARKER = "```mermaid"
_NATURAL_KEY_RE = re.compile(r"(\d+)")


def _natural_key(path: Path):
    """Sort key that treats embedded digit runs numerically (SPRINT_2 < SPRINT_10)."""
    return [int(p) if p.isdigit() else p for p in _NATURAL_KEY_RE.split(path.stem)]


def _summary_heading(moniker: str, summary: str) -> str:
    return f"# CHAT_{moniker} — Sprint Archive\n\n## Summary\n\n{summary.strip()}\n"


def _extract_mermaid_source(diagram_body: str) -> str | None:
    """Pull the raw text between the ```mermaid fence markers out of a
    rendered diagram_body (as produced by chat_diagram.render()/archive())."""
    start = diagram_body.find(FENCE_MARKER)
    if start == -1:
        return None
    start += len(FENCE_MARKER)
    end = diagram_body.find("```", start)
    if end == -1:
        return None
    return diagram_body[start:end].strip("\n")


def render_svg(mermaid_source: str, out_svg: Path) -> bool:
    """Render mermaid_source to out_svg via mermaid_render/ (real Chrome,
    not a syntax-only jsdom shim). Returns True on success. Never raises —
    every failure mode (no Node, deps not installed, no Chrome found,
    mermaid-cli itself failing) is a soft "can't do this right now," logged
    to stderr, so the caller can fall back to the live mermaid fence rather
    than aborting the whole archive operation over an optional feature."""
    if shutil.which("node") is None:
        print("chat-report --svg: 'node' not found on PATH — falling back to "
              "the live mermaid fence.", file=sys.stderr)
        return False

    node_modules = MERMAID_RENDER_DIR / "node_modules"
    if not node_modules.is_dir():
        print(f"chat-report --svg: installing mermaid_render dependencies "
              f"(first use) in {MERMAID_RENDER_DIR}...", file=sys.stderr)
        install = subprocess.run(["npm", "install"], cwd=MERMAID_RENDER_DIR,
                                  capture_output=True, text=True)
        if install.returncode != 0:
            print(f"chat-report --svg: 'npm install' failed, falling back to "
                  f"the live mermaid fence:\n{install.stderr}", file=sys.stderr)
            return False

    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_source)
        input_path = f.name
    try:
        result = subprocess.run(
            ["node", str(MERMAID_RENDER_DIR / "render.mjs"), input_path, str(out_svg)],
            capture_output=True, text=True, timeout=60,
        )
    finally:
        Path(input_path).unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"chat-report --svg: render failed, falling back to the live "
              f"mermaid fence:\n{result.stderr}", file=sys.stderr)
        return False
    return True


def archive(chat_file: Path, diagram_file: Path, archive_dir: Path,
            moniker: str, summary: str, force: bool = False, svg: bool = False) -> tuple[Path, Path]:
    """Archive chat_file/diagram_file under moniker, then reset chat_file in place."""
    text = chat_file.read_text()
    header, blocks = parse_blocks(text)
    if not blocks:
        print("Error: CHAT.md has no message blocks to archive.", file=sys.stderr)
        sys.exit(1)

    archive_md = archive_dir / f"CHAT_{moniker}.md"
    archive_diagram = archive_dir / f"CHAT_{moniker}.diagram.md"
    if not force:
        existing = [p for p in (archive_md, archive_diagram) if p.exists()]
        if existing:
            paths = ", ".join(str(p) for p in existing)
            print(f"Error: archive already exists for moniker '{moniker}': {paths}. "
                  f"Pass --force to overwrite.", file=sys.stderr)
            sys.exit(1)

    archive_dir.mkdir(parents=True, exist_ok=True)

    heading = _summary_heading(moniker, summary)
    archive_md.write_text(heading + "\n---\n" + BLOCK_SEP.join(blocks) + "\n")

    diagram_text = diagram_file.read_text() if diagram_file.exists() else chat_diagram.render(text)
    fence_at = diagram_text.find(FENCE_MARKER)
    diagram_body = diagram_text[fence_at:] if fence_at != -1 else diagram_text

    if svg:
        mermaid_source = _extract_mermaid_source(diagram_body)
        if mermaid_source is not None:
            archive_svg = archive_dir / f"CHAT_{moniker}.svg"
            if render_svg(mermaid_source, archive_svg):
                diagram_body = f"![CHAT_{moniker} diagram]({archive_svg.name})\n"

    archive_diagram.write_text(heading + "\n" + diagram_body)

    summary_first_line = summary.strip().splitlines()[0] if summary.strip() else ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pointer = (
        f"\n> **Previous sprint archived:** `agents/{ARCHIVE_DIRNAME}/CHAT_{moniker}.md` "
        f"({timestamp}) — {summary_first_line}\n"
    )
    chat_file.write_text(header.rstrip("\n") + "\n" + pointer + "\n---\n")
    chat_diagram.regenerate(chat_file, diagram_file)

    return archive_md, archive_diagram


def combine(archive_dir: Path, out_md: Path, out_diagram: Path) -> tuple[Path, Path]:
    """Concatenate every archived sprint in archive_dir into CHAT_FULL.md/.diagram.md."""
    md_archives = sorted(
        (p for p in archive_dir.glob("CHAT_*.md")
         if not p.name.endswith(".diagram.md") and p != out_md),
        key=_natural_key,
    )
    diagram_archives = sorted(
        (p for p in archive_dir.glob("CHAT_*.diagram.md") if p != out_diagram),
        key=_natural_key,
    )

    if not md_archives:
        print(f"Error: no archives found in {archive_dir}.", file=sys.stderr)
        sys.exit(1)

    md_body = "\n\n---\n\n".join(p.read_text().strip() for p in md_archives)
    out_md.write_text(
        "# CHAT_FULL — Combined Sprint History\n\n"
        "Auto-generated by `bobp chat-report --combine`. Do not edit by hand — "
        "regenerate after archiving a new sprint.\n\n---\n\n" + md_body + "\n"
    )

    diagram_body = "\n\n---\n\n".join(p.read_text().strip() for p in diagram_archives)
    out_diagram.write_text(
        "# CHAT_FULL — Combined Sprint Diagrams\n\n"
        "Auto-generated by `bobp chat-report --combine`. Do not edit by hand — "
        "regenerate after archiving a new sprint.\n\n---\n\n" + diagram_body + "\n"
    )

    return out_md, out_diagram


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive CHAT.md under a sprint moniker, or combine all archives.")
    parser.add_argument("--moniker", help="Sprint moniker, e.g. SPRINT_1 (archive mode)")
    parser.add_argument("--summary", help="Summary text for the archive heading (archive mode)")
    parser.add_argument("--summary-file", help="Read the summary from a file instead of --summary")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing archive for this moniker")
    parser.add_argument("--svg", action="store_true",
                         help="Also render the diagram to a standalone .svg (real Chrome + mermaid-cli) and "
                              "embed it as an image instead of a live ```mermaid fence. Falls back to the "
                              "fence with a warning if Node/Chrome aren't available.")
    parser.add_argument("--combine", action="store_true", help="Combine all archives into CHAT_FULL.md/.diagram.md")
    parser.add_argument("--chat-file", default=None, help="Path to CHAT.md (default: agents/CHAT.md)")
    parser.add_argument("--diagram-file", default=None, help="Path to CHAT.diagram.md (default: agents/CHAT.diagram.md)")
    parser.add_argument("--archive-dir", default=None, help="Archive directory (default: agents/chat_archive)")
    args = parser.parse_args()

    agents_dir = find_project_root() / "agents"
    chat_file = Path(args.chat_file or agents_dir / "CHAT.md")
    diagram_file = Path(args.diagram_file or agents_dir / "CHAT.diagram.md")
    archive_dir = Path(args.archive_dir or agents_dir / ARCHIVE_DIRNAME)

    if args.combine:
        if args.moniker or args.summary or args.summary_file:
            print("Error: --combine cannot be used with --moniker/--summary/--summary-file.", file=sys.stderr)
            sys.exit(1)
        out_md, out_diagram = combine(archive_dir, archive_dir / "CHAT_FULL.md", archive_dir / "CHAT_FULL.diagram.md")
        print(f"Wrote {out_md}")
        print(f"Wrote {out_diagram}")
        return

    if not args.moniker:
        print("Error: --moniker is required in archive mode.", file=sys.stderr)
        sys.exit(1)
    if args.summary and args.summary_file:
        print("Error: pass either --summary or --summary-file, not both.", file=sys.stderr)
        sys.exit(1)
    summary = args.summary or (Path(args.summary_file).read_text() if args.summary_file else None)
    if not summary or not summary.strip():
        print("Error: --summary or --summary-file is required in archive mode.", file=sys.stderr)
        sys.exit(1)

    if not chat_file.is_file():
        print(f"Error: Could not find {chat_file}", file=sys.stderr)
        sys.exit(1)

    archive_md, archive_diagram = archive(chat_file, diagram_file, archive_dir, args.moniker, summary,
                                           force=args.force, svg=args.svg)
    print(f"Wrote {archive_md}")
    print(f"Wrote {archive_diagram}")
    print(f"Reset {chat_file}")


if __name__ == "__main__":
    main()
