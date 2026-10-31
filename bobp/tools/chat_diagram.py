#!/usr/bin/env python3
"""
Render agents/CHAT.md as a Mermaid sequence diagram.

TLDR:
    Parses the `[<small>TS</small>] [**Persona**]->[**To**] *cmd*:` entries written
    by chat.py and renders them as a Mermaid sequenceDiagram (one arrow per
    persona -> recipient message), grouped with a date Note whenever the day
    changes. The diagram is split at phase, sprint, and epic boundaries: each
    boundary closes the diagram, adds a markdown close-out/next-phase section,
    and starts a new diagram. Writes agents/CHAT.diagram.md by default; `--print` writes to
    stdout instead. Build-status entries (persona "make") are skipped unless
    --include-builds is passed, since they're noise for following the
    persona-to-persona conversation.
    Called automatically by chat.py after every post; also runnable standalone
    (`bobp chat-diagram`) to regenerate on demand without posting a message.
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

MAX_MSG_LEN = 140  # hard safety cap on message length, applied before wrapping
WRAP_WIDTH = 24  # characters per line once wrapped. Message text now renders
# in a Note box (see build_diagram) rather than crammed against the arrow
# line, so it has more room than an inline label would — narrow enough to
# stay a compact vertical column, wide enough not to be needlessly tall.


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
    # Mermaid's sequence-diagram lexer treats a bare `;` as a statement
    # terminator even inside a quoted message (verified against mermaid
    # 11.16.0 directly: quoting does NOT protect a semicolon — the lexer's
    # quoted-string mode exits early at `;`, and everything after it,
    # including a later `<br/>`, gets mis-tokenized against the *unquoted*
    # grammar). Chat messages routinely contain semicolons mid-sentence
    # (e.g. "...consistency); new US-14..."), so replace them outright
    # rather than relying on quoting to protect them.
    text = text.replace(";", ",")
    if len(text) > MAX_MSG_LEN:
        text = text[: MAX_MSG_LEN - 1].rstrip() + "…"
    return text


def _wrap_label(text):
    """Word-wrap text to WRAP_WIDTH-char lines, joined with <br/> for a Mermaid label."""
    if not text:
        return text
    return "<br/>".join(textwrap.wrap(text, width=WRAP_WIDTH))


def _note_text_for(entry):
    """The message body (no cmd prefix) for the Note under an entry's arrow."""
    return _wrap_label(_clean_message(_first_line(entry.body)))


def _recap_details(entries):
    """Deterministic recap lines (`**Persona**: message`) for a loop boundary.

    Chat is intentionally not sent to an external summarizer. Prefer explicit
    outcome messages (passed, complete, approved, failed); if none exist, use
    the latest messages so the recap still records what closed the loop.
    """
    outcomes = [
        e for e in entries
        if re.search(r"\b(pass(?:ed)?|fail(?:ed)?|complete|completed|approved|reject(?:ed)?)\b",
                     _first_line(e.body), re.IGNORECASE)
    ]
    selected = (outcomes or entries)[-3:]
    return [
        f"- **{e.persona}**: {_clean_message(_first_line(e.body))}"
        for e in selected
        if _first_line(e.body)
    ]


def _recap_section(title, entries):
    """A markdown section recapping `entries`, or None when there is nothing to say."""
    details = _recap_details(entries) if entries else []
    if not details:
        return None
    return "\n".join([f"## {title}", ""] + details)


def _is_phase_marker(entry):
    return re.match(r"^phase\s+\S", entry.cmd, re.IGNORECASE) is not None


def _loop_close_kind(entry):
    cmd = entry.cmd.strip().lower()
    if cmd == "pm launch":
        return "Sprint"
    if re.fullmatch(r"(?:epic\s+)?(?:close|complete|completed|approve|approved)", cmd):
        return "Epic"
    return None


def _quote_label(label):
    """Wrap a Mermaid sequence-diagram message label in double quotes.

    Defense-in-depth for arbitrary punctuation in free-form chat text beyond
    the one character confirmed to actually need active handling (`;` —
    replaced with `,` in `_clean_message`, since quoting alone does not
    protect it; see that function's comment). Any literal double quote in the
    label is escaped with Mermaid's `#quot;` HTML-entity syntax so it can't
    end the quote early.
    """
    escaped = label.replace('"', "#quot;")
    return f'"{escaped}"'


# themeVariables.fontSize alone does not reliably control sequence-diagram
# message/note text (verified visually — bumping it did nothing on GitHub's
# render). Mermaid's sequence diagrams have their own dedicated font-size
# keys under the `sequence` config block; those are the ones that actually
# apply to arrow labels, actor names, and Note text respectively.
INIT_DIRECTIVE = (
    '%%{init: {"sequence": {'
    '"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14'
    "}}}%%"
)


def _segment_diagram(entries):
    """One Mermaid sequenceDiagram covering `entries`, declaring only its own participants."""
    participant_ids = {}
    order = []
    for e in entries:
        for name in [e.persona] + [r.strip() for r in e.to.split(",")]:
            display = _display_name(name)
            if display not in participant_ids:
                participant_ids[display] = _sanitize_id(display)
                order.append(display)

    lines = [INIT_DIRECTIVE, "sequenceDiagram", "    autonumber"]
    for display in order:
        pid = participant_ids[display]
        if pid == display:
            lines.append(f"    participant {pid}")
        else:
            lines.append(f'    participant {pid} as "{display}"')

    left, right = participant_ids[order[0]], participant_ids[order[-1]]
    last_date = None
    for e in entries:
        date = e.ts.split(" ")[0]
        if date != last_date:
            lines.append(f"    Note over {left},{right}: \U0001F4C5 {date}")
            last_date = date

        from_id = participant_ids[_display_name(e.persona)]
        cmd_label = _quote_label(e.cmd)
        note_text = _note_text_for(e)
        for recipient in (r.strip() for r in e.to.split(",")):
            to_id = participant_ids[_display_name(recipient)]
            # Keep the arrow label short (just the command) — it's rendered
            # right against the thin arrow line with little room. The full
            # message snippet goes in a Note underneath instead, which gets
            # its own box with far more room and its own (bigger) font size.
            #
            # `Note right of {from_id}` (not `Note over {from_id},{to_id}`) —
            # verified against mermaid's own renderer source that `Note over`
            # sizes its box as the literal x-distance between the two named
            # participants, so it spans every lane in between them. With 10+
            # participants and frequent broadcasts (`Cypher->>All`), that
            # produced near-full-diagram-width notes for any non-adjacent
            # pair — exactly the sprawl this redesign was meant to fix.
            # `Note right of` is anchored to the sender alone and sized from
            # the wrapped text, independent of how far the recipient is.
            lines.append(f"    {from_id}->>{to_id}: {cmd_label}")
            if note_text:
                lines.append(f"    Note right of {from_id}: {_quote_label(note_text)}")
    return "\n".join(lines)


def build_blocks(entries, include_builds=False):
    """Split the log into ordered ("diagram", mermaid) and ("text", markdown) blocks.

    The diagram closes at each phase boundary, sprint close, and epic close.
    A markdown section recaps the close-out and announces the next phase,
    and the following entries start a fresh sequenceDiagram.
    """
    filtered = [e for e in entries if include_builds or not _is_build_status(e)]

    if not filtered:
        return [("diagram", f"{INIT_DIRECTIVE}\nsequenceDiagram\n    Note over Team: No conversation entries yet.")]

    blocks = []
    segment = []

    def flush():
        if segment:
            blocks.append(("diagram", _segment_diagram(segment)))
            segment.clear()

    def text(markdown):
        if markdown:
            blocks.append(("text", markdown))

    phase_entries = []
    phase_label = None
    epic_entries = None
    for e in filtered:
        if epic_entries is not None and re.match(r"^plan\s+story\b", e.cmd.strip(), re.IGNORECASE):
            flush()
            text(_recap_section("Epic close-out", epic_entries))
            epic_entries = None

        if _is_phase_marker(e):
            flush()
            if phase_entries and phase_label:
                text(_recap_section(f"Phase {phase_label} close-out", phase_entries))
            phase_label = re.sub(r"^phase\s+", "", e.cmd, flags=re.IGNORECASE).strip()
            phase_entries = []
            start = [f"## Phase {phase_label} starts"]
            goal = _clean_message(_first_line(e.body))
            if goal:
                start += ["", goal]
            text("\n".join(start))

        segment.append(e)
        if not _is_phase_marker(e):
            phase_entries.append(e)
        close_kind = _loop_close_kind(e)
        if re.fullmatch(r"plan\s+epic", e.cmd.strip(), re.IGNORECASE):
            epic_entries = [e]
        elif epic_entries is not None:
            epic_entries.append(e)
        if close_kind:
            flush()
            if close_kind == "Sprint" and phase_entries and phase_label:
                text(_recap_section(f"Phase {phase_label} close-out", phase_entries[:-1]))
                phase_entries = []
                phase_label = None
            summary_entries = (epic_entries or [e]) if close_kind == "Epic" else [e]
            text(_recap_section(f"{close_kind} close-out", summary_entries))
            if close_kind == "Epic":
                epic_entries = None

    flush()
    if phase_entries and phase_label:
        text(_recap_section(f"Phase {phase_label} so far", phase_entries))
    return blocks


def render(chat_text, include_builds=False):
    """Render a full CHAT.diagram.md file (header, fenced mermaid blocks, phase recap sections) from CHAT.md text."""
    parts = [
        "# CHAT.md — Conversation Flow\n\n"
        "Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. "
        "Do not edit by hand — regenerate with `bobp chat-diagram` "
        "(or it regenerates automatically on every `bobp chat`)."
    ]
    for kind, body in build_blocks(parse_entries(chat_text), include_builds=include_builds):
        parts.append(f"```mermaid\n{body}\n```" if kind == "diagram" else body)
    return "\n\n".join(parts) + "\n"


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
