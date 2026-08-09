#!/usr/bin/env python3
"""
Render agents/CHAT.md as a Mermaid sequence diagram.

TLDR:
    Parses the `[<small>TS</small>] [**Persona**]->[**To**] *cmd*:` entries written
    by chat.py and renders them as a Mermaid sequenceDiagram (one arrow per
    persona -> recipient message), grouped with a date Note whenever the day
    changes. Writes agents/CHAT.diagram.md by default; `--print` writes to
    stdout instead. Build-status entries (persona "make") are skipped unless
    --include-builds is passed, since they're noise for following the
    persona-to-persona conversation.
    Called automatically by chat.py after every post; also runnable standalone
    (`make chat_diagram`) to regenerate on demand without posting a message.
"""

import argparse
import re
import sys
import textwrap
from collections import namedtuple

try:
    from ._common import find_project_root
except ImportError:
    from _common import find_project_root
from pathlib import Path

Entry = namedtuple("Entry", "ts persona to cmd body")

ENTRY_RE = re.compile(
    r"\[<small>(?P<ts>.+?)</small>\]\s*"
    r"\[\*\*(?P<persona>.+?)\*\*\]->\[\*\*(?P<to>.+?)\*\*\]\s*"
    r"\*(?P<cmd>.+?)\*:\s*\n"
    r"(?P<body>.*?)(?=\n---\n\[<small>|\Z)",
    re.DOTALL,
)

MAX_MSG_LEN = 300  # hard safety cap on message length, applied before wrapping
WRAP_WIDTH = 40  # characters per line once wrapped for the diagram label


def parse_entries(text):
    """Parse every `[persona]->[to] *cmd*: body` block out of a CHAT.md-formatted string."""
    entries = []
    for m in ENTRY_RE.finditer(text):
        entries.append(
            Entry(
                ts=m.group("ts").strip(),
                persona=m.group("persona").strip(),
                to=m.group("to").strip(),
                cmd=m.group("cmd").strip(),
                body=m.group("body").strip(),
            )
        )
    return entries


def _is_build_status(entry):
    return entry.persona.lower() == "make"


def _sanitize_id(name):
    safe = re.sub(r"\W", "_", name)
    if not safe or safe[0].isdigit():
        safe = f"P_{safe}"
    return safe


def _display_name(name):
    return "All" if name.lower() == "all" else name


def _first_line(body):
    for line in body.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _clean_message(text):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_MSG_LEN:
        text = text[: MAX_MSG_LEN - 1].rstrip() + "…"
    return text


def _wrap_label(text):
    """Word-wrap text to WRAP_WIDTH-char lines, joined with <br/> for a Mermaid label."""
    if not text:
        return text
    return "<br/>".join(textwrap.wrap(text, width=WRAP_WIDTH))


def _label_for(entry):
    snippet = _wrap_label(_clean_message(_first_line(entry.body)))
    return f"{entry.cmd} — {snippet}" if snippet else entry.cmd


def build_diagram(entries, include_builds=False):
    """Render the parsed entries as a Mermaid sequenceDiagram body (no code fence)."""
    filtered = [e for e in entries if include_builds or not _is_build_status(e)]

    if not filtered:
        return "sequenceDiagram\n    Note over Team: No conversation entries yet."

    participant_ids = {}
    order = []
    for e in filtered:
        for name in [e.persona] + [r.strip() for r in e.to.split(",")]:
            display = _display_name(name)
            if display not in participant_ids:
                participant_ids[display] = _sanitize_id(display)
                order.append(display)

    lines = ["sequenceDiagram", "    autonumber"]
    for display in order:
        pid = participant_ids[display]
        if pid == display:
            lines.append(f"    participant {pid}")
        else:
            lines.append(f'    participant {pid} as "{display}"')

    left, right = participant_ids[order[0]], participant_ids[order[-1]]
    last_date = None
    for e in filtered:
        date = e.ts.split(" ")[0]
        if date != last_date:
            lines.append(f"    Note over {left},{right}: \U0001F4C5 {date}")
            last_date = date

        from_id = participant_ids[_display_name(e.persona)]
        label = _label_for(e)
        recipients = [r.strip() for r in e.to.split(",")]
        for recipient in recipients:
            to_id = participant_ids[_display_name(recipient)]
            lines.append(f"    {from_id}->>{to_id}: {label}")

    return "\n".join(lines)


def render(chat_text, include_builds=False):
    """Render a full CHAT.diagram.md file (header + fenced mermaid block) from CHAT.md text."""
    diagram = build_diagram(parse_entries(chat_text), include_builds=include_builds)
    return (
        "# CHAT.md — Conversation Flow\n\n"
        "Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. "
        "Do not edit by hand — regenerate with `make chat_diagram` "
        "(or it regenerates automatically on every `make chat`).\n\n"
        f"```mermaid\n{diagram}\n```\n"
    )


def regenerate(chat_file, diagram_file, include_builds=False):
    """Read chat_file and (re)write diagram_file. Used as a post-write hook by chat.py."""
    chat_file, diagram_file = Path(chat_file), Path(diagram_file)
    text = chat_file.read_text()
    diagram_file.write_text(render(text, include_builds=include_builds))


def main():
    parser = argparse.ArgumentParser(description="Render agents/CHAT.md as a Mermaid sequence diagram")
    parser.add_argument("--chat-file", default=None, help="Path to CHAT.md (default: agents/CHAT.md)")
    parser.add_argument("--out", default=None, help="Output path (default: agents/CHAT.diagram.md)")
    parser.add_argument("--include-builds", action="store_true", help="Include 'make' build-status entries")
    parser.add_argument("--print", dest="print_only", action="store_true", help="Print to stdout instead of writing a file")
    args = parser.parse_args()

    if args.chat_file is None or args.out is None:
        agents_dir = find_project_root() / "agents"
        args.chat_file = args.chat_file or str(agents_dir / "CHAT.md")
        args.out = args.out or str(agents_dir / "CHAT.diagram.md")

    chat_path = Path(args.chat_file)
    if not chat_path.is_file():
        print(f"Error: Could not find {chat_path}")
        sys.exit(1)

    output = render(chat_path.read_text(), include_builds=args.include_builds)

    if args.print_only:
        print(output)
        return

    out_path = Path(args.out)
    out_path.write_text(output)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
