#!/usr/bin/env python3
"""bobp merge — conflict-safe merging for timestamped Markdown documents.

TLDR:
    Replaces `bobp chat-merge` with a single stdlib tool that resolves Git
    conflicts and orders timestamped Markdown entries across CHAT.md,
    date-headed logs (e.g. LESSONS.md), and metadata-dated logs (e.g.
    DECISIONS.md / ADRs). Supports both post-conflict cleanup on a working-tree
    file and an optional Git custom merge driver (`--git-driver %O %A %B`).
    All file reads and writes enforce SEC-005/006 regular-file safety
    (O_NOFOLLOW | O_NONBLOCK + fstat S_ISREG, bounded 10 MiB read, strict
    UTF-8), and untrusted paths/snippets are sanitized before terminal output.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

CHAT_DEFAULT = Path("agents/CHAT.md")
BLOCK_SEP = "\n---\n"
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MiB hard cap (SEC-005)
MAX_ECHO = 120
METADATA_WINDOW_LINES = 12

# Style 1: CHAT.md blocks
TS_FULL_RE = re.compile(
    r"^(\[<small>)(\d{4}-\d{2}-\d{2})[ ](\d{2}:\d{2}:\d{2})(</small>\])"
)
TS_DATE_RE = re.compile(r"^(\[<small>)(\d{4}-\d{2}-\d{2})(</small>\])")

# Style 2 & 3: ATX headings and ISO dates (linear-time, single-line [ \t] only)
ATX_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+)$")
ISO_DATE_RE = re.compile(
    r"(?<!\d)(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?(?!\d)"
)
META_DATE_RE = re.compile(
    r"^(?:[-*][ \t]+)?(?:\*\*)?Date(?:\*\*)?[ \t]*:[ \t]*(?:\*\*[ \t]*)?"
    r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?",
    re.IGNORECASE,
)

# Git conflict markers (exact 7-char prefixes)
CONFLICT_START_RE = re.compile(r"^<{7}(?:[ \t].*)?$")
CONFLICT_BASE_RE = re.compile(r"^\|{7}(?:[ \t].*)?$")
CONFLICT_SEP_RE = re.compile(r"^={7}$")
CONFLICT_END_RE = re.compile(r"^>{7}(?:[ \t].*)?$")
CONFLICT_MARKER_RE = re.compile(
    r"^(?:<{7}(?:[ \t].*)?|\|{7}(?:[ \t].*)?|={7}|>{7}(?:[ \t].*)?)$",
    re.MULTILINE,
)

HELP_EPILOG = """\
Supported timestamped Markdown styles (auto-detected):
  chat      CHAT.md blocks separated by '---' starting with [<small>YYYY-MM-DD[ HH:MM:SS]</small>]
  heading   ATX headings containing an ISO date (e.g. '## [2026-11-01] Title')
  metadata  ATX headings with a leading Date field (e.g. '* **Date**: 2026-11-01' or 'Date: ...')

Opt-in Git custom merge driver setup (never modified automatically):
  # .git/config  (or: git config merge.bobp.driver "bobp merge --git-driver %O %A %B")
  [merge "bobp"]
      name = Bob Protocol timestamped Markdown merge driver
      driver = bobp merge --git-driver %O %A %B

  # .gitattributes
  agents/CHAT.md merge=bobp
  docs/LESSONS.md merge=bobp
  docs/DECISIONS.md merge=bobp

Exit codes:
  0  Clean merge, no-op, or resolvable --dry-run
  1  Unresolvable conflict (preamble or same-entry edit) or file/parse error
  2  Invalid CLI usage
"""


class MergeError(Exception):
    """User-facing runtime, I/O, or parse error (exits 1)."""


@dataclass
class Entry:
    timestamp: datetime | None
    inferred: bool
    key: str
    raw: str


@dataclass
class Document:
    style: str  # "chat" | "heading" | "metadata"
    preamble: str
    entries: list[Entry]
    level: int = 0  # ATX heading level for heading/metadata styles


# ---------------------------------------------------------------------------
# SEC-005 / SEC-006 / SEC-007 safe I/O and terminal sanitization
# ---------------------------------------------------------------------------

def sanitize(text: str, limit: int = MAX_ECHO) -> str:
    """Strip Unicode control/format chars (ESC, BEL, BiDi) and cap length."""
    cleaned = "".join(ch for ch in text if not unicodedata.category(ch).startswith("C"))
    return cleaned if len(cleaned) <= limit else cleaned[:limit] + "..."


def read_regular_file(path: Path, max_bytes: int | None = None) -> tuple[bytes, str]:
    """Read a regular UTF-8 file without following symlinks or blocking on FIFOs."""
    limit = MAX_FILE_BYTES if max_bytes is None else max_bytes
    label = sanitize(str(path), limit=256)
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise MergeError(f"Cannot open {label}: {exc.strerror or exc}") from exc

    chunks: list[bytes] = []
    total = 0
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise MergeError(f"Refusing non-regular file {label}")
        while True:
            chunk = os.read(fd, min(65536, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                raise MergeError(
                    f"Refusing {label}: file exceeds {limit}-byte size limit"
                )
    except OSError as exc:
        raise MergeError(f"Cannot read {label}: {exc.strerror or exc}") from exc
    finally:
        os.close(fd)

    raw = b"".join(chunks)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MergeError(f"Refusing {label}: file is not valid UTF-8") from exc
    return raw, text


def write_regular_file(
    path: Path,
    data: bytes,
    *,
    create: bool = False,
    mode: int = 0o644,
) -> None:
    """Write bytes to a regular file without following symlinks or blocking on FIFOs."""
    label = sanitize(str(path), limit=256)
    flags = os.O_WRONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    if create:
        flags |= os.O_CREAT
    try:
        fd = os.open(path, flags, mode)
    except OSError as exc:
        raise MergeError(f"Cannot open {label} for writing: {exc.strerror or exc}") from exc

    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise MergeError(f"Refusing to write non-regular file {label}")
        os.ftruncate(fd, 0)
        view = memoryview(data)
        written = 0
        while written < len(view):
            n = os.write(fd, view[written:])
            if n <= 0:
                raise MergeError(f"Short write on {label}")
            written += n
        os.fsync(fd)
    except OSError as exc:
        raise MergeError(f"Cannot write {label}: {exc.strerror or exc}") from exc
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# Timestamp helpers and conflict-marker handling
# ---------------------------------------------------------------------------

def _parse_iso_dt(date_part: str, time_part: str | None) -> tuple[datetime | None, bool]:
    """Parse YYYY-MM-DD (+ optional HH:MM:SS); return (None, False) on invalid calendar date."""
    try:
        if time_part:
            return datetime.fromisoformat(f"{date_part} {time_part}"), False
        return datetime.fromisoformat(f"{date_part} 00:00:00"), True
    except ValueError:
        return None, False


def strip_conflict_markers(text: str) -> tuple[str, int]:
    """Remove complete Git conflict-marker lines (including line endings), keeping both sides."""
    kept: list[str] = []
    count = 0
    for line in text.splitlines(keepends=True):
        if CONFLICT_MARKER_RE.match(line.rstrip("\r\n")):
            count += 1
            continue
        kept.append(line)
    clean = "".join(kept)
    if count:
        clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean, count


# ---------------------------------------------------------------------------
# Style 1 (chat) exports — preserved for bobp/tools/chat_report.py
# ---------------------------------------------------------------------------

def parse_blocks(text: str) -> tuple[str, list[str]]:
    """Return (header, [block, ...]) where each CHAT.md block starts with its timestamp line."""
    first = re.search(r"(?:^|\n)---\n+(?=\[<small>\d{4}-\d{2}-\d{2})", text)
    if first is None:
        first = re.search(r"(?:^|\n)(?=\[<small>\d{4}-\d{2}-\d{2})", text)
    if first:
        header = text[: first.start()]
        body = text[first.start() :]
    else:
        header = ""
        body = text

    stripped_body = body.lstrip("\n")
    if stripped_body.startswith("---"):
        after_sep = stripped_body[3:]
        if after_sep.startswith("\n") or after_sep == "":
            stripped_body = after_sep.lstrip("\n")
    raw = re.split(r"(?<!\n)\n+(?:---\n+)?(?=\[<small>\d{4}-\d{2}-\d{2})", stripped_body)
    blocks = [b for b in raw if b.strip()]
    # Only count as chat blocks if at least one block matches a chat timestamp
    if not any(block_ts(b)[0] is not None for b in blocks):
        return header, []
    return header, blocks


def block_ts(block: str) -> tuple[datetime | None, bool]:
    """Return (datetime, is_inferred) for a CHAT.md block."""
    first = block.split("\n", 1)[0]
    m = TS_FULL_RE.match(first)
    if m:
        return _parse_iso_dt(m.group(2), m.group(3))
    m = TS_DATE_RE.match(first)
    if m:
        return _parse_iso_dt(m.group(2), None)
    return None, False


def _rewrite_chat_ts(block: str, assigned: datetime) -> str:
    """Replace date-only CHAT.md timestamp with inferred full datetime."""
    first, *rest = block.split("\n", 1)
    m = TS_DATE_RE.match(first)
    if m:
        new_ts = assigned.strftime("%Y-%m-%d %H:%M:%S")
        new_first = m.group(1) + new_ts + m.group(3) + first[m.end() :]
        return new_first + ("\n" + rest[0] if rest else "")
    return block


def _interpolate_chat_entries(entries: list[Entry]) -> tuple[list[Entry], int]:
    """Assign interpolated datetimes to date-only CHAT.md entries between dated neighbors."""
    n = len(entries)
    resolved: list[tuple[datetime, bool, Entry]] = []
    for e in entries:
        if e.timestamp is None:
            resolved.append((datetime(2000, 1, 1), True, e))
        else:
            resolved.append((e.timestamp, e.inferred, e))

    out: list[Entry] = []
    inferred_count = 0
    i = 0
    while i < n:
        dt, inferred, e = resolved[i]
        if not inferred:
            out.append(e)
            i += 1
            continue

        run_start = i
        while i < n and resolved[i][1]:
            i += 1
        run_end = i
        run_len = run_end - run_start

        t_before = resolved[run_start - 1][0] if run_start > 0 else None
        t_after = resolved[run_end][0] if run_end < n else None

        for j in range(run_start, run_end):
            orig_dt, _, orig_entry = resolved[j]
            if t_before is None and t_after is None:
                assigned = orig_dt
            elif t_before is None:
                offset = run_len - (j - run_start)
                assigned = t_after - timedelta(minutes=offset)
            elif t_after is None:
                assigned = t_before + timedelta(minutes=(j - run_start + 1))
            else:
                span = (t_after - t_before).total_seconds()
                step = span / (run_len + 1)
                assigned = t_before + timedelta(seconds=step * (j - run_start + 1))

            rewritten = _rewrite_chat_ts(orig_entry.raw, assigned)
            was_rewritten = rewritten != orig_entry.raw
            if was_rewritten:
                inferred_count += 1
            key = rewritten.split("\n", 1)[0].strip()
            out.append(Entry(timestamp=assigned, inferred=True, key=key, raw=rewritten))

    return out, inferred_count


# ---------------------------------------------------------------------------
# Style 2 (heading) & Style 3 (metadata) parsing
# ---------------------------------------------------------------------------

def _heading_date(line: str) -> tuple[int, datetime | None, bool]:
    """If line is an ATX heading carrying a valid ISO date, return (level, dt, date_only)."""
    m = ATX_HEADING_RE.match(line)
    if not m:
        return 0, None, False
    level = len(m.group(1))
    dm = ISO_DATE_RE.search(m.group(2))
    if not dm:
        return level, None, False
    dt, date_only = _parse_iso_dt(dm.group(1), dm.group(2))
    return level, dt, date_only


def _metadata_date(lines: list[str], start_idx: int) -> tuple[datetime | None, bool]:
    """Scan leading metadata block (up to METADATA_WINDOW_LINES) after heading at start_idx."""
    end = min(len(lines), start_idx + 1 + METADATA_WINDOW_LINES)
    for idx in range(start_idx + 1, end):
        line = lines[idx]
        if ATX_HEADING_RE.match(line):
            break
        mm = META_DATE_RE.match(line.strip())
        if mm:
            dt, date_only = _parse_iso_dt(mm.group(1), mm.group(2))
            if dt is not None:
                return dt, date_only
    return None, False


def _parse_chat_doc(text: str) -> Document | None:
    header, blocks = parse_blocks(text)
    if not blocks:
        return None
    entries: list[Entry] = []
    for b in blocks:
        dt, inferred = block_ts(b)
        key = b.split("\n", 1)[0].strip()
        entries.append(Entry(timestamp=dt, inferred=inferred, key=key, raw=b.strip("\n")))
    return Document(style="chat", preamble=header, entries=entries, level=0)


def _parse_heading_doc(text: str) -> Document | None:
    lines = text.splitlines()
    entry_level = 0
    starts: list[tuple[int, datetime, bool]] = []

    for i, line in enumerate(lines):
        level, dt, date_only = _heading_date(line)
        if dt is None:
            continue
        if entry_level == 0:
            entry_level = level
        if level == entry_level:
            starts.append((i, dt, date_only))

    if not starts:
        return None

    preamble = "\n".join(lines[: starts[0][0]])
    entries: list[Entry] = []
    for idx, (line_no, dt, _date_only) in enumerate(starts):
        end_no = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        raw = "\n".join(lines[line_no:end_no]).strip("\n")
        key = lines[line_no].strip()
        entries.append(Entry(timestamp=dt, inferred=False, key=key, raw=raw))
    return Document(style="heading", preamble=preamble, entries=entries, level=entry_level)


def _parse_metadata_doc(text: str) -> Document | None:
    lines = text.splitlines()
    entry_level = 0
    starts: list[tuple[int, datetime, bool]] = []

    for i, line in enumerate(lines):
        m = ATX_HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        if entry_level != 0 and level != entry_level:
            continue
        dt, date_only = _metadata_date(lines, i)
        if dt is None:
            continue
        if entry_level == 0:
            entry_level = level
        starts.append((i, dt, date_only))

    if not starts:
        return None

    preamble = "\n".join(lines[: starts[0][0]])
    entries: list[Entry] = []
    for idx, (line_no, dt, _date_only) in enumerate(starts):
        end_no = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        raw = "\n".join(lines[line_no:end_no]).strip("\n")
        key = lines[line_no].strip()
        entries.append(Entry(timestamp=dt, inferred=False, key=key, raw=raw))
    return Document(style="metadata", preamble=preamble, entries=entries, level=entry_level)


def parse_document(text: str, preferred_style: str | None = None) -> Document | None:
    """Detect and parse a timestamped Markdown document (chat -> heading -> metadata)."""
    parsers = {
        "chat": _parse_chat_doc,
        "heading": _parse_heading_doc,
        "metadata": _parse_metadata_doc,
    }
    order = (
        [preferred_style] + [s for s in ("chat", "heading", "metadata") if s != preferred_style]
        if preferred_style in parsers
        else ["chat", "heading", "metadata"]
    )
    for name in order:
        doc = parsers[name](text)
        if doc is not None:
            return doc
    return None


# ---------------------------------------------------------------------------
# Conflict hunk inspection (preamble conflict guard)
# ---------------------------------------------------------------------------

def _is_entry_start(lines: list[str], idx: int, style: str, level: int) -> bool:
    """True if lines[idx] begins a recognizable entry for (style, level)."""
    line = lines[idx]
    if style == "chat":
        if TS_FULL_RE.match(line) or TS_DATE_RE.match(line):
            return True
        if line.strip() == "---":
            # Look ahead to next non-blank line
            for nxt in range(idx + 1, min(len(lines), idx + 3)):
                if not lines[nxt].strip():
                    continue
                return bool(TS_FULL_RE.match(lines[nxt]) or TS_DATE_RE.match(lines[nxt]))
        return False
    if style == "heading":
        lvl, dt, _ = _heading_date(line)
        return dt is not None and lvl == level
    if style == "metadata":
        m = ATX_HEADING_RE.match(line)
        if not m or len(m.group(1)) != level:
            return False
        dt, _ = _metadata_date(lines, idx)
        return dt is not None
    return False


def _side_starts_at_entry(side_lines: list[str], style: str, level: int) -> bool:
    """True if a conflict side is empty/blank or its first non-blank line starts an entry."""
    for idx, line in enumerate(side_lines):
        if not line.strip():
            continue
        return _is_entry_start(side_lines, idx, style, level)
    return True


def has_preamble_conflict(text: str, style: str, level: int) -> bool:
    """Return True if a Git conflict hunk touches the preamble before timestamped entries.

    A top-of-file conflict hunk immediately preceding entries where every non-empty
    branch side starts cleanly at an entry boundary (e.g. newest-first logs or
    newly-reset CHAT.md) is NOT a preamble conflict.
    """
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        if CONFLICT_START_RE.match(lines[i]):
            sides: list[list[str]] = [[]]
            i += 1
            while i < n and not CONFLICT_END_RE.match(lines[i]):
                if CONFLICT_BASE_RE.match(lines[i]) or CONFLICT_SEP_RE.match(lines[i]):
                    sides.append([])
                else:
                    sides[-1].append(lines[i])
                i += 1
            if i < n:
                i += 1  # consume >>>>>>>

            # Check every non-empty side: all must begin at an entry boundary
            any_non_empty = False
            for side in sides:
                if any(ln.strip() for ln in side):
                    any_non_empty = True
                    if not _side_starts_at_entry(side, style, level):
                        return True
            if any_non_empty:
                # Valid top-of-file entry conflict: entries have begun
                return False
            continue

        if _is_entry_start(lines, i, style, level):
            return False
        i += 1
    return False


# ---------------------------------------------------------------------------
# Deduplication, ordering, and document reconstruction
# ---------------------------------------------------------------------------

def dedup_entries(entries: list[Entry]) -> tuple[list[Entry], int]:
    """Drop entries with identical stripped text (first occurrence wins)."""
    seen: set[str] = set()
    out: list[Entry] = []
    dupes = 0
    for e in entries:
        norm = e.raw.strip()
        if norm in seen:
            dupes += 1
            continue
        seen.add(norm)
        out.append(e)
    return out, dupes


def infer_order(entries: list[Entry]) -> str:
    """Infer 'asc' (oldest-first) or 'desc' (newest-first) from dated entries."""
    dated = [e.timestamp for e in entries if e.timestamp is not None and not e.inferred]
    if len(dated) < 2:
        return "asc"
    asc_pairs = sum(1 for a, b in zip(dated, dated[1:]) if a < b)
    desc_pairs = sum(1 for a, b in zip(dated, dated[1:]) if a > b)
    return "desc" if desc_pairs > asc_pairs else "asc"


def _strip_conflict_hunks(text: str) -> str:
    """Remove conflict hunks entirely (used to infer order from non-conflicted context)."""
    lines = text.splitlines()
    kept: list[str] = []
    in_hunk = False
    for line in lines:
        if CONFLICT_START_RE.match(line):
            in_hunk = True
            continue
        if in_hunk:
            if CONFLICT_END_RE.match(line):
                in_hunk = False
            continue
        kept.append(line)
    return "\n".join(kept)


def sort_entries(entries: list[Entry], direction: str) -> list[Entry]:
    """Stable chronological sort in 'asc' or 'desc' direction."""
    epoch = datetime(2000, 1, 1)
    return sorted(entries, key=lambda e: e.timestamp or epoch, reverse=(direction == "desc"))


def reconstruct_document(style: str, preamble: str, entries: list[Entry]) -> str:
    """Rebuild document text preserving preamble verbatim."""
    pre = preamble.rstrip("\n")
    if not entries:
        return f"{pre}\n" if pre else ""
    if style == "chat":
        body = "\n\n---\n".join(e.raw.strip("\n") for e in entries)
        if pre:
            return f"{pre}\n\n---\n{body}\n"
        return f"---\n{body}\n"
    body = "\n\n".join(e.raw.strip("\n") for e in entries)
    if pre:
        return f"{pre}\n\n{body}\n"
    return f"{body}\n"


# ---------------------------------------------------------------------------
# Post-conflict cleanup flow (Flow A)
# ---------------------------------------------------------------------------

def merge_file(
    path: Path,
    *,
    order: str = "auto",
    dry_run: bool = False,
    backup: bool = False,
) -> int:
    """Run post-conflict cleanup on a single file. Returns process exit code."""
    orig_bytes, orig_text = read_regular_file(path)
    stripped, marker_count = strip_conflict_markers(orig_text)

    doc = parse_document(stripped)
    if doc is None or not doc.entries:
        raise MergeError(
            f"No recognizable timestamped entries found in {sanitize(str(path), 256)} "
            "(expected CHAT.md, date-headed sections, or Date: metadata sections)."
        )

    if marker_count and has_preamble_conflict(orig_text, doc.style, doc.level):
        raise MergeError(
            f"Unresolvable preamble conflict in {sanitize(str(path), 256)}: "
            "conflict markers appear inside non-entry header text; resolve manually."
        )

    entries, dupe_count = dedup_entries(doc.entries)
    inferred_count = 0
    if doc.style == "chat":
        entries, inferred_count = _interpolate_chat_entries(entries)

    if order == "auto":
        if marker_count:
            # Infer order only from non-conflicted context; never from Git's arbitrary ours/theirs order
            context_doc = parse_document(
                _strip_conflict_hunks(orig_text), preferred_style=doc.style
            )
            direction = infer_order(context_doc.entries) if context_doc else "asc"
        else:
            direction = infer_order(entries)
    else:
        direction = order

    orig_order_keys = [id(e) for e in entries]
    sorted_entries = sort_entries(entries, direction)
    reordered_count = sum(
        1 for orig_id, e in zip(orig_order_keys, sorted_entries) if id(e) != orig_id
    )

    output = reconstruct_document(doc.style, doc.preamble, sorted_entries)
    changed = output != orig_text
    label = sanitize(str(path), 256)

    if dry_run:
        if not changed:
            print(
                f"No changes needed ({doc.style}, {direction}, {len(sorted_entries)} entries)."
            )
            return 0
        for e in sorted_entries:
            first_line = sanitize(e.raw.split("\n", 1)[0], 70)
            if e.inferred and doc.style == "chat" and e.timestamp:
                print(f"  [inferred -> {e.timestamp:%H:%M:%S}] {first_line}")
        print(
            f"Would merge {label} ({doc.style}, {direction}): {len(sorted_entries)} entries · "
            f"{inferred_count} timestamps inferred · {reordered_count} reordered · "
            f"{marker_count} conflict markers stripped · {dupe_count} duplicates removed"
        )
        return 0

    if not changed:
        print(f"No changes needed ({doc.style}, {direction}, {len(sorted_entries)} entries).")
        return 0

    if backup:
        bak_path = path.with_name(path.name + ".bak")
        write_regular_file(bak_path, orig_bytes, create=True)

    write_regular_file(path, output.encode("utf-8"), create=False)
    print(
        f"Merged {label} ({doc.style}, {direction}): {len(sorted_entries)} entries "
        f"({inferred_count} timestamps inferred, {reordered_count} reordered, "
        f"{marker_count} conflict markers stripped, {dupe_count} duplicates removed)."
    )
    if backup:
        print(f"Backup: {sanitize(str(path.with_name(path.name + '.bak')), 256)}")
    return 0


# ---------------------------------------------------------------------------
# Git custom merge driver flow (Flow B — --git-driver BASE OURS THEIRS)
# ---------------------------------------------------------------------------

def _index_entries(entries: list[Entry]) -> dict[str, list[Entry]]:
    indexed: dict[str, list[Entry]] = {}
    for e in entries:
        indexed.setdefault(e.key, []).append(e)
    return indexed


def _parse_driver_side(text: str, style: str, level: int) -> Document:
    """Parse one side of a 3-way merge using the already-detected style."""
    if not text.strip():
        return Document(style=style, preamble="", entries=[], level=level)
    doc = parse_document(text, preferred_style=style)
    if doc is not None and doc.style == style:
        return doc
    return Document(style=style, preamble=text.rstrip("\n"), entries=[], level=level)


def _infer_driver_order(ours: Document, theirs: Document, base: Document) -> str:
    """Infer asc/desc order with fallback chain: ours -> theirs -> base -> asc."""
    for doc in (ours, theirs, base):
        dated = [e for e in doc.entries if e.timestamp is not None and not e.inferred]
        if len(dated) >= 2:
            return infer_order(doc.entries)
    return "asc"


def _format_conflict_block(ours_raw: str | None, theirs_raw: str | None) -> str:
    ours_part = f"{ours_raw}\n" if ours_raw else ""
    theirs_part = f"{theirs_raw}\n" if theirs_raw else ""
    return f"<<<<<<< ours\n{ours_part}=======\n{theirs_part}>>>>>>> theirs"


def merge_git_driver(
    base_path: Path,
    ours_path: Path,
    theirs_path: Path,
    *,
    order: str = "auto",
) -> int:
    """3-way Git custom merge driver (%O %A %B). Writes merged result to ours_path.

    Returns 0 on clean merge, 1 on preamble or same-entry content conflict.
    Raises MergeError on I/O, SEC-005, or unrecognized-document errors (leaving ours untouched).
    """
    _, base_text = read_regular_file(base_path)
    _, ours_text = read_regular_file(ours_path)
    _, theirs_text = read_regular_file(theirs_path)

    # Detect style from ours -> theirs -> base
    ref_doc = None
    for sample in (ours_text, theirs_text, base_text):
        if sample.strip():
            candidate = parse_document(sample)
            if candidate is not None and candidate.entries:
                ref_doc = candidate
                break
    if ref_doc is None:
        raise MergeError(
            "No recognizable timestamped entries found in BASE, OURS, or THEIRS."
        )

    style, level = ref_doc.style, ref_doc.level
    base_doc = _parse_driver_side(base_text, style, level)
    ours_doc = _parse_driver_side(ours_text, style, level)
    theirs_doc = _parse_driver_side(theirs_text, style, level)

    has_conflict = False

    # 3-way preamble merge
    p_base = base_doc.preamble.rstrip("\n")
    p_ours = ours_doc.preamble.rstrip("\n")
    p_theirs = theirs_doc.preamble.rstrip("\n")
    if p_ours == p_theirs:
        merged_preamble = p_ours
    elif p_ours == p_base:
        merged_preamble = p_theirs
    elif p_theirs == p_base:
        merged_preamble = p_ours
    else:
        merged_preamble = _format_conflict_block(p_ours, p_theirs)
        has_conflict = True

    # 3-way entry merge keyed by entry identity
    base_map = _index_entries(base_doc.entries)
    ours_map = _index_entries(ours_doc.entries)
    theirs_map = _index_entries(theirs_doc.entries)

    all_keys: list[str] = []
    seen_keys: set[str] = set()
    for src in (ours_doc.entries, theirs_doc.entries, base_doc.entries):
        for e in src:
            if e.key not in seen_keys:
                seen_keys.add(e.key)
                all_keys.append(e.key)

    merged_entries: list[Entry] = []
    for key in all_keys:
        b_list = base_map.get(key, [])
        o_list = ours_map.get(key, [])
        t_list = theirs_map.get(key, [])

        if len(b_list) <= 1 and len(o_list) <= 1 and len(t_list) <= 1:
            b = b_list[0] if b_list else None
            o = o_list[0] if o_list else None
            t = t_list[0] if t_list else None
            b_raw = b.raw.strip() if b else None
            o_raw = o.raw.strip() if o else None
            t_raw = t.raw.strip() if t else None

            if o_raw == t_raw:
                if o is not None:
                    merged_entries.append(o)
            elif o_raw == b_raw:
                if t is not None:
                    merged_entries.append(t)
            elif t_raw == b_raw:
                if o is not None:
                    merged_entries.append(o)
            else:
                ref_entry = o or t or b
                conflict_raw = _format_conflict_block(o_raw, t_raw)
                merged_entries.append(
                    Entry(
                        timestamp=ref_entry.timestamp if ref_entry else None,
                        inferred=False,
                        key=key,
                        raw=conflict_raw,
                    )
                )
                has_conflict = True
        else:
            # Duplicate-key fallback: exact-body 3-way union honoring clean deletions
            b_raws = {e.raw.strip() for e in b_list}
            o_raws = {e.raw.strip() for e in o_list}
            t_raws = {e.raw.strip() for e in t_list}
            kept_raws: set[str] = set()
            for e in o_list:
                r = e.raw.strip()
                if r in b_raws and r not in t_raws:
                    continue  # cleanly deleted in theirs
                if r not in kept_raws:
                    kept_raws.add(r)
                    merged_entries.append(e)
            for e in t_list:
                r = e.raw.strip()
                if r in b_raws and r not in o_raws:
                    continue  # cleanly deleted in ours
                if r not in kept_raws:
                    kept_raws.add(r)
                    merged_entries.append(e)

    merged_entries, _ = dedup_entries(merged_entries)
    if style == "chat":
        merged_entries, _ = _interpolate_chat_entries(merged_entries)

    direction = (
        _infer_driver_order(ours_doc, theirs_doc, base_doc) if order == "auto" else order
    )
    sorted_entries = sort_entries(merged_entries, direction)
    output = reconstruct_document(style, merged_preamble, sorted_entries)
    write_regular_file(ours_path, output.encode("utf-8"), create=False)
    return 1 if has_conflict else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bobp merge",
        description=(
            "Resolve Git conflicts and order timestamped Markdown documents "
            "(CHAT.md, LESSONS.md, DECISIONS.md, ADR logs)."
        ),
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "path",
        nargs="?",
        default=None,
        help=f"Path to timestamped Markdown file (default: {CHAT_DEFAULT})",
    )
    p.add_argument(
        "--git-driver",
        nargs=3,
        metavar=("BASE", "OURS", "THEIRS"),
        help="Run as a Git custom merge driver (%%O %%A %%B), writing merged result to OURS",
    )
    p.add_argument(
        "--order",
        choices=("auto", "asc", "desc"),
        default="auto",
        help="Chronological entry order (default: auto-detected from document)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying the file (cleanup mode only)",
    )
    p.add_argument(
        "--backup",
        action="store_true",
        help="Write a <path>.bak backup before modifying (cleanup mode only)",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.git_driver is not None:
        if args.path is not None:
            parser.error("cannot combine positional PATH with --git-driver")
        if args.dry_run:
            parser.error("--dry-run cannot be used with --git-driver")
        if args.backup:
            parser.error("--backup cannot be used with --git-driver")
        base_p, ours_p, theirs_p = (Path(p) for p in args.git_driver)
        try:
            rc = merge_git_driver(base_p, ours_p, theirs_p, order=args.order)
        except MergeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        if rc != 0:
            sys.exit(rc)
        return

    target = Path(args.path) if args.path is not None else CHAT_DEFAULT
    try:
        rc = merge_file(
            target,
            order=args.order,
            dry_run=args.dry_run,
            backup=args.backup,
        )
    except MergeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
