"""Notify-only check that a project was set up by the running bobp (or newer).

TLDR:
    check(subcommand) is called by bobp.cli before every subcommand except
    install/update. It finds the project (an agents/ dir at or above the cwd),
    reads agents/.bobp-version, and if that version is missing, unreadable or
    older than the running bobp, prints ONE line to stderr naming both
    versions and the exact `bobp update <project>` command. It never prompts,
    never reads stdin, never writes to the project, and never raises: the
    subcommand always runs with its normal output and exit code.

    The stamp is untrusted text (it can arrive with a cloned repo), so it is
    only parsed for leading integers; anything echoed back has control
    characters stripped and is length-capped, and the project path in the
    printed command is shell-quoted. Set BOBP_NO_VERSION_CHECK=1 to disable.
"""

import os
import re
import shlex
import stat
import sys
import unicodedata
from pathlib import Path

from ._common import STAMP_NAME, find_project_root_or_none

SKIP_SUBCOMMANDS = frozenset({"install", "update"})
ENV_SWITCH = "BOBP_NO_VERSION_CHECK"
MAX_ECHO = 40
MAX_STAMP_BYTES = 256

_VERSION_RE = re.compile(r"^\s*v?(\d+(?:\.\d+)*)")


def parse_version(text: str) -> "tuple[int, ...] | None":
    """Leading dot-separated integers of `text` (0.3.0rc1 -> (0, 3, 0)), else None."""
    match = _VERSION_RE.match(text)
    if match is None:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def is_older(recorded: "tuple[int, ...]", current: "tuple[int, ...]") -> bool:
    """True if `recorded` < `current`, treating missing components as zero."""
    width = max(len(recorded), len(current))
    pad = lambda v: v + (0,) * (width - len(v))  # noqa: E731
    return pad(recorded) < pad(current)


def sanitize(text: str, limit: int = MAX_ECHO) -> str:
    """Drop control/format characters (terminal-escape defence) and cap the length."""
    cleaned = "".join(ch for ch in text if not unicodedata.category(ch).startswith("C"))
    return cleaned if len(cleaned) <= limit else cleaned[:limit] + "..."


def _read_stamp(root: Path) -> "str | None":
    """First line of the stamp, or None if absent, unreadable or not a plain file.

    The stamp may come from a cloned repo, so it is opened without following
    symlinks and without blocking (a symlink to /dev/stdin or a FIFO would
    otherwise hang every bobp command, SEC-005), and only a regular file counts.
    """
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(root / "agents" / STAMP_NAME, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        raw = os.read(fd, MAX_STAMP_BYTES)
    except OSError:
        return None
    finally:
        os.close(fd)
    lines = raw.decode("utf-8", errors="replace").splitlines()
    return lines[0] if lines else ""


def _disabled(env) -> bool:
    value = env.get(ENV_SWITCH, "")
    return value not in ("", "0")


def _notice(recorded_text: "str | None", current_text: str, root: Path) -> str:
    recorded = parse_version(recorded_text) if recorded_text is not None else None
    if recorded is None:
        was = "an unrecorded bobp version"
    else:
        was = f"bobp {sanitize(recorded_text.strip())}"
    project = shlex.quote(sanitize(str(root), limit=4096))
    return (
        f"bobp: this project was set up with {was}; installed is bobp "
        f"{sanitize(current_text)}. Run: bobp update {project}"
    )


def check(subcommand: str, *, start: "Path | None" = None, env=None, err=None) -> None:
    """Print the update notice if the project is behind; never raises, never blocks."""
    try:
        if subcommand in SKIP_SUBCOMMANDS:
            return
        env = os.environ if env is None else env
        if _disabled(env):
            return
        root = find_project_root_or_none(start)
        if root is None:
            return

        import bobp

        current_text = bobp.__version__
        current = parse_version(current_text)
        if current is None:
            return
        recorded_text = _read_stamp(root)
        recorded = parse_version(recorded_text) if recorded_text is not None else None
        if recorded is not None and not is_older(recorded, current):
            return

        stream = sys.stderr if err is None else err
        print(_notice(recorded_text, current_text, root), file=stream, flush=True)
    except Exception:  # noqa: BLE001 - the check must never affect the subcommand
        return
