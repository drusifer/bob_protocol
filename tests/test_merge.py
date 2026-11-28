"""Tests for `bobp merge` (`bobp/tools/merge.py`)."""

import io
import os
import shutil
import signal
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import pytest

from bobp import cli
from bobp.tools import merge as merge_mod


# ---------------------------------------------------------------------------
# Sample fixtures
# ---------------------------------------------------------------------------

CLEAN_CHAT = """# Chat Log

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 First message.

---
[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**Neo**] *qa handoff*:
 Second message.
"""

CONFLICTED_CHAT = """# Chat Log

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 First message.

<<<<<<< HEAD
---
[<small>2026-04-12 12:06:00</small>] [**Morpheus**]->[**Neo**] *lead handoff*:
 From branch A (later).
=======
---
[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**Neo**] *qa handoff*:
 From branch B (earlier).
>>>>>>> feature-branch
"""

TOP_CONFLICT_CHAT = """# Chat Log

<<<<<<< HEAD
---
[<small>2026-04-12 12:06:00</small>] [**Morpheus**]->[**Neo**] *lead handoff*:
 From branch A.
=======
---
[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**Neo**] *qa handoff*:
 From branch B.
>>>>>>> feature-branch
"""

DATE_ONLY_CHAT = """# Chat Log

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**all**] *note*:
 Anchor before.

---
[<small>2026-04-12</small>] [**Trin**]->[**all**] *note*:
 Date-only entry.

---
[<small>2026-04-12 12:10:00</small>] [**Morpheus**]->[**all**] *note*:
 Anchor after.
"""

LESSONS_DESC_CONFLICTED = """# Project Lessons Learned

Standing rules for all agents.

---

<<<<<<< HEAD
## [2026-11-27] Branch A Lesson

### Context
Added on HEAD.
=======
## [2026-11-28] Branch B Lesson

### Context
Added on feature branch.
>>>>>>> feature-branch

## [2026-11-05] Existing Newer Lesson

### Context
Second newest.

## [2026-11-01] Existing Older Lesson

### Context
Oldest lesson.
"""

ADR_LOG_CONFLICTED = """# Architecture Decision Records

Project decision log.

# ADR-0001: Use SQLite

*   **Status**: Accepted
*   **Deciders**: Morpheus
*   **Date**: 2026-10-01

## 1. Context
Initial storage choice.

<<<<<<< HEAD
# ADR-0003: Add Caching

- **Status:** Proposed
- **Date:** 2026-10-20 14:30:00

## 1. Context
Cache hot queries.
=======
# ADR-0002: Pin Toolchains

Date: 2026-10-10

## 1. Context
Pin python and node.
>>>>>>> feature-branch
"""

PREAMBLE_CONFLICT = """# Lessons Learned
<<<<<<< HEAD
Intro version A.
=======
Intro version B.
>>>>>>> feature-branch

## [2026-11-01] First Lesson

### Context
Body.
"""


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = cli.main(argv)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------------------
# CLI registration & help / usage contract (STORY-MRG-1 AC1, AC4)
# ---------------------------------------------------------------------------

def test_cli_registers_merge_and_removes_chat_merge():
    assert "merge" in cli.SUBCOMMANDS
    assert "chat-merge" not in cli.SUBCOMMANDS
    rc, _, err = _run_cli(["chat-merge"])
    assert rc != 0
    assert "unknown subcommand" in err.lower()


def test_help_exits_zero_with_exit_codes_and_no_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = list(tmp_path.rglob("*"))
    rc, out, err = _run_cli(["merge", "--help"])
    assert rc == 0
    assert "bobp merge" in out
    assert "--git-driver" in out
    assert "--order" in out
    assert "--dry-run" in out
    assert "--backup" in out
    assert ".git/config" in out
    assert ".gitattributes" in out
    assert "%O %A %B" in out
    assert "0" in out and "1" in out and "2" in out
    assert list(tmp_path.rglob("*")) == before
    assert err == ""


def test_multiple_positional_files_exit_2_without_modifying_files(tmp_path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text(CLEAN_CHAT)
    b.write_text(CLEAN_CHAT)
    rc, _, err = _run_cli(["merge", str(a), str(b)])
    assert rc == 2
    assert "bobp merge" in err
    assert a.read_text() == CLEAN_CHAT
    assert b.read_text() == CLEAN_CHAT


# ---------------------------------------------------------------------------
# Style 1: CHAT.md (STORY-MRG-1 AC2, AC3, AC4)
# ---------------------------------------------------------------------------

def test_chat_conflicted_merge_strips_markers_dedups_and_sorts(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(CONFLICTED_CHAT)

    rc, out, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "<<<<<<<" not in result
    assert "=======" not in result
    assert ">>>>>>>" not in result
    assert result.index("From branch B (earlier).") < result.index("From branch A (later).")
    assert "chat" in out.lower() and "asc" in out.lower()
    # ADR-S4-3: no .bak by default
    assert not path.with_name(path.name + ".bak").exists()
    assert not path.with_suffix(".md.bak").exists()


def test_chat_top_of_file_conflict_is_not_false_preamble_conflict(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(TOP_CONFLICT_CHAT)

    rc, _, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "<<<<<<<" not in result
    assert result.index("From branch B.") < result.index("From branch A.")


def test_chat_date_only_interpolation_preserved(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(DATE_ONLY_CHAT)

    rc, out, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "[<small>2026-04-12 12:05:00</small>]" in result
    assert "1 timestamp" in out.lower() or "inferred" in out.lower()


def test_chat_diff3_markers_and_exact_dupes_cleaned(tmp_path):
    text = (
        "# Chat\n\n"
        "<<<<<<< HEAD\n"
        "---\n[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**all**] *note*:\n Same.\n"
        "||||||| base\n"
        "---\n[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**all**] *note*:\n Same.\n"
        "=======\n"
        "---\n[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**all**] *note*:\n Same.\n"
        ">>>>>>> other\n"
    )
    path = tmp_path / "CHAT.md"
    path.write_text(text)

    rc, _, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "|||||||" not in result
    assert result.count("Same.") == 1


def test_parse_blocks_and_block_sep_exported_for_chat_report():
    header, blocks = merge_mod.parse_blocks(CLEAN_CHAT)
    assert "# Chat Log" in header
    assert len(blocks) == 2
    assert merge_mod.BLOCK_SEP == "\n---\n"


# ---------------------------------------------------------------------------
# Style 2: Heading-dated logs (LESSONS.md) (STORY-MRG-1 AC2, AC3, AC4)
# ---------------------------------------------------------------------------

def test_lessons_desc_top_of_file_conflict_preserves_preamble_divider_and_subheadings(tmp_path):
    path = tmp_path / "LESSONS.md"
    path.write_text(LESSONS_DESC_CONFLICTED)

    rc, out, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "<<<<<<<" not in result
    # Preamble divider preserved exactly once
    assert result.count("\n---\n") == 1
    # Inferred desc order: 2026-11-28 -> 2026-11-27 -> 2026-11-05 -> 2026-11-01
    assert "heading" in out.lower() and "desc" in out.lower()
    idx_28 = result.index("## [2026-11-28] Branch B Lesson")
    idx_27 = result.index("## [2026-11-27] Branch A Lesson")
    idx_05 = result.index("## [2026-11-05] Existing Newer Lesson")
    idx_01 = result.index("## [2026-11-01] Existing Older Lesson")
    assert idx_28 < idx_27 < idx_05 < idx_01
    # Subheading stayed attached to its parent lesson
    assert result.index("Added on feature branch.") < idx_27


def test_order_override_asc_and_same_date_ties_preserved(tmp_path):
    text = (
        "# Lessons\n\n"
        "## [2026-11-27] Second Same-Day Lesson\n\nBody B.\n\n"
        "## [2026-11-27] First Same-Day Lesson\n\nBody A.\n\n"
        "## [2026-11-01] Earlier Lesson\n\nBody old.\n"
    )
    path = tmp_path / "LESSONS.md"
    path.write_text(text)

    rc, out, err = _run_cli(["merge", str(path), "--order", "asc"])
    assert rc == 0, err
    result = path.read_text()
    assert "asc" in out.lower()
    assert result.index("Earlier Lesson") < result.index("Second Same-Day Lesson")
    # Both same-day lessons preserved deterministically
    assert "First Same-Day Lesson" in result
    assert "Second Same-Day Lesson" in result
    assert result.index("Second Same-Day Lesson") < result.index("First Same-Day Lesson")


# ---------------------------------------------------------------------------
# Style 3: Metadata-dated ADRs / DECISIONS.md (STORY-MRG-1 AC2, AC3)
# ---------------------------------------------------------------------------

def test_adr_metadata_dates_all_variants_and_subheadings(tmp_path):
    path = tmp_path / "DECISIONS.md"
    path.write_text(ADR_LOG_CONFLICTED)

    rc, out, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    result = path.read_text()
    assert "<<<<<<<" not in result
    assert "metadata" in out.lower() and "asc" in out.lower()
    idx_1 = result.index("# ADR-0001: Use SQLite")
    idx_2 = result.index("# ADR-0002: Pin Toolchains")
    idx_3 = result.index("# ADR-0003: Add Caching")
    assert idx_1 < idx_2 < idx_3
    # Subheading stayed inside ADR-0002
    assert idx_2 < result.index("Pin python and node.") < idx_3


def test_invalid_calendar_date_does_not_crash(tmp_path):
    text = "# Notes\n\n## [2026-02-30] Impossible Date\n\nBody.\n"
    path = tmp_path / "BAD_DATE.md"
    path.write_text(text)

    rc, _, err = _run_cli(["merge", str(path)])
    assert rc == 1
    assert path.read_text() == text
    assert err.strip() != ""


# ---------------------------------------------------------------------------
# Preamble conflict, dry-run, no-op, opt-in --backup (STORY-MRG-1 AC4, AC5)
# ---------------------------------------------------------------------------

def test_preamble_conflict_refuses_and_leaves_file_untouched(tmp_path):
    path = tmp_path / "LESSONS.md"
    path.write_text(PREAMBLE_CONFLICT)

    rc, _, err = _run_cli(["merge", str(path)])
    assert rc == 1
    assert "preamble" in err.lower()
    assert path.read_text() == PREAMBLE_CONFLICT


def test_preamble_conflict_dry_run_also_exits_1(tmp_path):
    path = tmp_path / "LESSONS.md"
    path.write_text(PREAMBLE_CONFLICT)

    rc, _, err = _run_cli(["merge", str(path), "--dry-run"])
    assert rc == 1
    assert "preamble" in err.lower()
    assert path.read_text() == PREAMBLE_CONFLICT


def test_dry_run_previews_without_writing(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(CONFLICTED_CHAT)

    rc, out, err = _run_cli(["merge", str(path), "--dry-run"])
    assert rc == 0, err
    assert path.read_text() == CONFLICTED_CHAT
    assert "chat" in out.lower() and "asc" in out.lower()


def test_clean_file_is_noop(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(CLEAN_CHAT)
    mtime_before = path.stat().st_mtime_ns

    rc, out, err = _run_cli(["merge", str(path)])
    assert rc == 0, err
    assert "no changes needed" in out.lower()
    assert path.stat().st_mtime_ns == mtime_before


def test_opt_in_backup_writes_bak_with_original_content(tmp_path):
    path = tmp_path / "CHAT.md"
    path.write_text(CONFLICTED_CHAT)

    rc, _, err = _run_cli(["merge", str(path), "--backup"])
    assert rc == 0, err
    bak = path.with_name(path.name + ".bak")
    assert bak.exists()
    assert bak.read_text() == CONFLICTED_CHAT
    assert "<<<<<<<" not in path.read_text()


# ---------------------------------------------------------------------------
# Security regressions: SEC-005, SEC-006, SEC-007 (Switch Gate 2b checklist)
# ---------------------------------------------------------------------------

def test_missing_file_and_unrecognized_file_exit_1(tmp_path):
    missing = tmp_path / "missing.md"
    rc, _, err = _run_cli(["merge", str(missing)])
    assert rc == 1
    assert "missing.md" in err

    plain = tmp_path / "plain.md"
    plain.write_text("# Just a README\n\nNo timestamps here.\n")
    rc2, _, err2 = _run_cli(["merge", str(plain)])
    assert rc2 == 1
    assert plain.read_text() == "# Just a README\n\nNo timestamps here.\n"
    assert err2.strip() != ""


def test_symlink_target_rejected_untouched(tmp_path):
    real = tmp_path / "real.md"
    real.write_text(CONFLICTED_CHAT)
    link = tmp_path / "link.md"
    link.symlink_to(real)

    rc, _, err = _run_cli(["merge", str(link)])
    assert rc == 1
    assert real.read_text() == CONFLICTED_CHAT
    assert err.strip() != ""


def test_fifo_target_rejected_without_blocking(tmp_path):
    fifo = tmp_path / "pipe.md"
    os.mkfifo(fifo)

    def _timeout(_signum, _frame):
        raise TimeoutError("bobp merge hung on FIFO!")

    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(3)
    try:
        rc, _, err = _run_cli(["merge", str(fifo)])
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)

    assert rc == 1
    assert err.strip() != ""


def test_backup_refuses_planted_symlink_and_fifo_before_touching_target(tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("SECRET_DO_NOT_OVERWRITE")
    target = tmp_path / "CHAT.md"
    target.write_text(CONFLICTED_CHAT)
    bak = target.with_name(target.name + ".bak")
    bak.symlink_to(victim)

    rc, _, err = _run_cli(["merge", str(target), "--backup"])
    assert rc == 1
    assert victim.read_text() == "SECRET_DO_NOT_OVERWRITE"
    assert target.read_text() == CONFLICTED_CHAT
    assert err.strip() != ""

    # Also test FIFO at .bak
    bak.unlink()
    os.mkfifo(bak)

    def _timeout(_signum, _frame):
        raise TimeoutError("bobp merge --backup hung on FIFO!")

    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(3)
    try:
        rc2, _, err2 = _run_cli(["merge", str(target), "--backup"])
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)

    assert rc2 == 1
    assert target.read_text() == CONFLICTED_CHAT
    assert err2.strip() != ""


def test_oversized_and_invalid_utf8_files_rejected_untouched(tmp_path, monkeypatch):
    # Oversized (cap monkeypatched to small size for fast test)
    big = tmp_path / "big.md"
    big.write_text(CONFLICTED_CHAT)
    monkeypatch.setattr(merge_mod, "MAX_FILE_BYTES", 64)
    rc, _, err = _run_cli(["merge", str(big)])
    assert rc == 1
    assert big.read_text() == CONFLICTED_CHAT
    assert "size" in err.lower() or "large" in err.lower() or "limit" in err.lower()

    # Invalid UTF-8 binary file
    monkeypatch.setattr(merge_mod, "MAX_FILE_BYTES", 10 * 1024 * 1024)
    raw = b"\xff\xfe\x00\x01binary garbage"
    bad = tmp_path / "bad.md"
    bad.write_bytes(raw)
    rc2, _, err2 = _run_cli(["merge", str(bad)])
    assert rc2 == 1
    assert bad.read_bytes() == raw
    assert "utf-8" in err2.lower()


def test_terminal_escape_sequences_sanitized_in_output(tmp_path):
    evil_name = tmp_path / "bad\x1b[31m\x07name.md"
    rc, out, err = _run_cli(["merge", str(evil_name)])
    assert rc == 1
    assert "\x1b" not in err and "\x07" not in err
    assert "\x1b" not in out and "\x07" not in out

    # Also check dry-run entry preview sanitization (with date-only entry so preview executes)
    esc_chat = (
        "# Chat\n\n"
        "---\n[<small>2026-04-12 12:00:00</small>] [**Neo\x1b[31m**]->[**all**] *note*:\n A.\n\n"
        "---\n[<small>2026-04-12</small>] [**Trin\x07\x1b[31m**]->[**all**] *note*:\n B.\n\n"
        "---\n[<small>2026-04-12 12:10:00</small>] [**Morpheus**]->[**all**] *note*:\n C.\n"
    )
    path = tmp_path / "CHAT.md"
    path.write_text(esc_chat)
    rc2, out2, err2 = _run_cli(["merge", str(path), "--dry-run"])
    assert rc2 == 0
    assert "[inferred ->" in out2
    assert "\x1b" not in out2 and "\x07" not in out2
    assert "\x1b" not in err2 and "\x07" not in err2


def test_meta_date_regex_is_linear_time_no_redos():
    """SEC-008 regression: META_DATE_RE must not backtrack quadratically on long whitespace."""
    evil_line = "Date:" + (" " * 50_000) + "x"

    def _timeout(_signum, _frame):
        raise TimeoutError("META_DATE_RE ReDoS timeout!")

    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(2)
    try:
        assert merge_mod.META_DATE_RE.match(evil_line) is None
        # SEC-009 regression: parse_blocks must not backtrack quadratically on blank-line runs
        _, blocks = merge_mod.parse_blocks("a" + "\n" * 50_000 + "x")
        assert blocks == []
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def test_chat_git_factored_separator_mid_file_and_top_of_file(tmp_path):
    """Morpheus review regression: Git factors shared '---' above <<<<<<< HEAD in CHAT.md."""
    mid_file = (
        "# Chat Log\n\n"
        "---\n[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**all**] *note*:\n Base.\n\n"
        "---\n"
        "<<<<<<< HEAD\n"
        "[<small>2026-04-12 12:06:00</small>] [**Morpheus**]->[**all**] *note*:\n Branch A.\n"
        "=======\n"
        "[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**all**] *note*:\n Branch B.\n"
        ">>>>>>> feature\n"
    )
    p1 = tmp_path / "MID_CHAT.md"
    p1.write_text(mid_file)
    rc1, _, err1 = _run_cli(["merge", str(p1)])
    assert rc1 == 0, err1
    r1 = p1.read_text()
    assert r1.count("\n---\n") == 3
    assert r1.index("Base.") < r1.index("Branch B.") < r1.index("Branch A.")

    top_file = (
        "# Chat Log\n\n"
        "---\n"
        "<<<<<<< HEAD\n"
        "[<small>2026-04-12 12:06:00</small>] [**Morpheus**]->[**all**] *note*:\n Branch A.\n"
        "=======\n"
        "[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**all**] *note*:\n Branch B.\n"
        ">>>>>>> feature\n"
    )
    p2 = tmp_path / "TOP_CHAT.md"
    p2.write_text(top_file)
    rc2, _, err2 = _run_cli(["merge", str(p2)])
    assert rc2 == 0, err2
    r2 = p2.read_text()
    assert r2.count("\n---\n") == 2
    assert r2.index("Branch B.") < r2.index("Branch A.")


# ---------------------------------------------------------------------------
# Phase 2: Optional Git custom merge driver (--git-driver BASE OURS THEIRS)
# ---------------------------------------------------------------------------

def test_git_driver_rejects_conflicting_cli_flags(tmp_path):
    base = tmp_path / "base.md"
    ours = tmp_path / "ours.md"
    theirs = tmp_path / "theirs.md"
    for p in (base, ours, theirs):
        p.write_text(CLEAN_CHAT)

    rc1, _, err1 = _run_cli(["merge", str(base), "--git-driver", str(base), str(ours), str(theirs)])
    assert rc1 == 2 and "bobp merge" in err1

    rc2, _, err2 = _run_cli(["merge", "--dry-run", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc2 == 2 and "bobp merge" in err2

    rc3, _, err3 = _run_cli(["merge", "--backup", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc3 == 2 and "bobp merge" in err3


def test_git_driver_additive_entries_clean_merge_and_no_bak(tmp_path):
    base_txt = (
        "# Lessons\n\n"
        "## [2026-11-05] Existing Newer\n\nBody 2.\n\n"
        "## [2026-11-01] Existing Older\n\nBody 1.\n"
    )
    ours_txt = (
        "# Lessons\n\n"
        "## [2026-11-10] Ours Entry\n\nFrom ours.\n\n"
        "## [2026-11-05] Existing Newer\n\nBody 2.\n\n"
        "## [2026-11-01] Existing Older\n\nBody 1.\n"
    )
    theirs_txt = (
        "# Lessons\n\n"
        "## [2026-11-12] Theirs Entry\n\nFrom theirs.\n\n"
        "## [2026-11-05] Existing Newer\n\nBody 2.\n\n"
        "## [2026-11-01] Existing Older\n\nBody 1.\n"
    )
    base, ours, theirs = tmp_path / "base.md", tmp_path / "ours.md", tmp_path / "theirs.md"
    base.write_text(base_txt)
    ours.write_text(ours_txt)
    theirs.write_text(theirs_txt)

    rc, _, err = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc == 0, err
    res = ours.read_text()
    assert "<<<<<<<" not in res
    assert res.index("Theirs Entry") < res.index("Ours Entry") < res.index("Existing Newer") < res.index("Existing Older")
    assert not ours.with_name(ours.name + ".bak").exists()


def test_git_driver_empty_base_and_direction_fallback_to_theirs(tmp_path):
    base = tmp_path / "base.md"
    ours = tmp_path / "ours.md"
    theirs = tmp_path / "theirs.md"
    base.write_text("")
    ours.write_text("# Lessons\n\n## [2026-11-03] Ours Only\n\nOurs.\n")
    theirs.write_text(
        "# Lessons\n\n"
        "## [2026-11-10] Theirs New\n\nNew.\n\n"
        "## [2026-11-01] Theirs Old\n\nOld.\n"
    )

    rc, _, err = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc == 0, err
    res = ours.read_text()
    # Direction falls back to theirs -> desc
    assert res.index("Theirs New") < res.index("Ours Only") < res.index("Theirs Old")


def test_git_driver_honors_single_side_edit_and_deletion(tmp_path):
    base_txt = (
        "# Decisions\n\n"
        "# ADR-0001: First\n\n* **Date**: 2026-10-01\n\nOriginal A.\n\n"
        "# ADR-0002: Second\n\n* **Date**: 2026-10-02\n\nOriginal B.\n"
    )
    # Ours edits ADR-0001; theirs deletes ADR-0002
    ours_txt = (
        "# Decisions\n\n"
        "# ADR-0001: First\n\n* **Date**: 2026-10-01\n\nUpdated A.\n\n"
        "# ADR-0002: Second\n\n* **Date**: 2026-10-02\n\nOriginal B.\n"
    )
    theirs_txt = (
        "# Decisions\n\n"
        "# ADR-0001: First\n\n* **Date**: 2026-10-01\n\nOriginal A.\n"
    )
    base, ours, theirs = tmp_path / "b.md", tmp_path / "o.md", tmp_path / "t.md"
    base.write_text(base_txt)
    ours.write_text(ours_txt)
    theirs.write_text(theirs_txt)

    rc, _, err = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc == 0, err
    res = ours.read_text()
    assert "Updated A." in res
    assert "ADR-0002" not in res


def test_git_driver_same_entry_and_preamble_conflicts_emit_markers_and_exit_1(tmp_path):
    base_txt = "# Lessons\n\n## [2026-11-01] Shared\n\nBase body.\n"
    ours_txt = "# Lessons\n\n## [2026-11-01] Shared\n\nOurs body.\n"
    theirs_txt = "# Lessons\n\n## [2026-11-01] Shared\n\nTheirs body.\n"
    base, ours, theirs = tmp_path / "b.md", tmp_path / "o.md", tmp_path / "t.md"
    base.write_text(base_txt)
    ours.write_text(ours_txt)
    theirs.write_text(theirs_txt)

    rc, _, _ = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc == 1
    res = ours.read_text()
    assert "<<<<<<< ours" in res and "=======" in res and ">>>>>>> theirs" in res
    assert "Ours body." in res and "Theirs body." in res

    # Preamble conflict
    base.write_text("# Title\n\n## [2026-11-01] Entry\n\nSame.\n")
    ours.write_text("# Title Ours\n\n## [2026-11-01] Entry\n\nSame.\n")
    theirs.write_text("# Title Theirs\n\n## [2026-11-01] Entry\n\nSame.\n")
    rc2, _, _ = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc2 == 1
    res2 = ours.read_text()
    assert "<<<<<<< ours" in res2 and "Title Ours" in res2 and "Title Theirs" in res2

    # Delete-vs-modify conflict
    base.write_text("# Lessons\n\n## [2026-11-01] Entry\n\nBase.\n\n## [2026-11-02] Keep\n\nKeep.\n")
    ours.write_text("# Lessons\n\n## [2026-11-02] Keep\n\nKeep.\n")
    theirs.write_text("# Lessons\n\n## [2026-11-01] Entry\n\nModified.\n\n## [2026-11-02] Keep\n\nKeep.\n")
    rc3, _, _ = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc3 == 1
    res3 = ours.read_text()
    assert "<<<<<<< ours" in res3 and "Modified." in res3


def test_git_driver_sec005_rejects_missing_symlink_fifo_and_unrecognized(tmp_path):
    base = tmp_path / "base.md"
    ours = tmp_path / "ours.md"
    theirs = tmp_path / "theirs.md"
    base.write_text(CLEAN_CHAT)
    ours.write_text(CLEAN_CHAT)
    theirs.write_text(CLEAN_CHAT)

    # Symlink on theirs
    link = tmp_path / "link.md"
    link.symlink_to(theirs)
    rc, _, err = _run_cli(["merge", "--git-driver", str(base), str(ours), str(link)])
    assert rc == 1 and err.strip() != ""
    assert ours.read_text() == CLEAN_CHAT

    # FIFO on base (alarm-guarded)
    fifo = tmp_path / "pipe.md"
    os.mkfifo(fifo)

    def _timeout(_signum, _frame):
        raise TimeoutError("bobp merge --git-driver hung on FIFO!")

    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(3)
    try:
        rc2, _, err2 = _run_cli(["merge", "--git-driver", str(fifo), str(ours), str(theirs)])
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    assert rc2 == 1 and err2.strip() != ""
    assert ours.read_text() == CLEAN_CHAT

    # Unrecognized documents
    for p in (base, ours, theirs):
        p.write_text("plain text without timestamps\n")
    rc3, _, err3 = _run_cli(["merge", "--git-driver", str(base), str(ours), str(theirs)])
    assert rc3 == 1 and err3.strip() != ""
    assert ours.read_text() == "plain text without timestamps\n"


@pytest.mark.skipif(shutil.which("git") is None, reason="git binary not installed")
def test_real_git_merge_driver_end_to_end(tmp_path):
    """STORY-MRG-2 AC4: verify real `git merge` across CHAT.md, LESSONS.md, and DECISIONS.md."""
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_AUTHOR_NAME": "Tester",
        "GIT_AUTHOR_EMAIL": "tester@example.com",
        "GIT_COMMITTER_NAME": "Tester",
        "GIT_COMMITTER_EMAIL": "tester@example.com",
        "BOBP_NO_VERSION_CHECK": "1",
    }

    def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=check,
        )

    git("init", "-b", "main")
    driver_cmd = f'"{sys.executable}" -m bobp.cli merge --git-driver %O %A %B'
    git("config", "merge.bobp.name", "Bob Protocol timestamped merge driver")
    git("config", "merge.bobp.driver", driver_cmd)

    (repo / ".gitattributes").write_text(
        "CHAT.md merge=bobp\nLESSONS.md merge=bobp\nDECISIONS.md merge=bobp\n"
    )
    (repo / "CHAT.md").write_text(CLEAN_CHAT)
    (repo / "LESSONS.md").write_text(
        "# Lessons\n\n## [2026-11-05] Existing New\n\nNew.\n\n## [2026-11-01] Existing Old\n\nOld.\n"
    )
    (repo / "DECISIONS.md").write_text(
        "# Decisions\n\n# ADR-0001: Init\n\n* **Date**: 2026-10-01\n\nBase ADR.\n"
    )
    git("add", ".")
    git("commit", "-m", "base")

    # Branch A adds entries to all 3 docs
    git("checkout", "-b", "branch-a")
    (repo / "CHAT.md").write_text(
        CLEAN_CHAT
        + "\n---\n[<small>2026-04-12 12:20:00</small>] [**Morpheus**]->[**all**] *note*:\n From A.\n"
    )
    (repo / "LESSONS.md").write_text(
        "# Lessons\n\n## [2026-11-10] Lesson A\n\nFrom A.\n\n"
        "## [2026-11-05] Existing New\n\nNew.\n\n## [2026-11-01] Existing Old\n\nOld.\n"
    )
    (repo / "DECISIONS.md").write_text(
        "# Decisions\n\n# ADR-0001: Init\n\n* **Date**: 2026-10-01\n\nBase ADR.\n\n"
        "# ADR-0003: From A\n\n- **Date:** 2026-10-20\n\nBody A.\n"
    )
    git("commit", "-am", "branch-a additions")

    # Main adds different entries to all 3 docs
    git("checkout", "main")
    (repo / "CHAT.md").write_text(
        CLEAN_CHAT
        + "\n---\n[<small>2026-04-12 12:15:00</small>] [**Neo**]->[**all**] *note*:\n From main.\n"
    )
    (repo / "LESSONS.md").write_text(
        "# Lessons\n\n## [2026-11-12] Lesson Main\n\nFrom main.\n\n"
        "## [2026-11-05] Existing New\n\nNew.\n\n## [2026-11-01] Existing Old\n\nOld.\n"
    )
    (repo / "DECISIONS.md").write_text(
        "# Decisions\n\n# ADR-0001: Init\n\n* **Date**: 2026-10-01\n\nBase ADR.\n\n"
        "# ADR-0002: From Main\n\nDate: 2026-10-10\n\nBody Main.\n"
    )
    git("commit", "-am", "main additions")

    # Additive merge must succeed automatically with exit 0!
    res = git("merge", "branch-a", "--no-edit", check=False)
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"

    chat_res = (repo / "CHAT.md").read_text()
    assert "<<<<<<<" not in chat_res
    assert chat_res.index("From main.") < chat_res.index("From A.")

    lessons_res = (repo / "LESSONS.md").read_text()
    assert "<<<<<<<" not in lessons_res
    assert lessons_res.index("Lesson Main") < lessons_res.index("Lesson A") < lessons_res.index("Existing New")

    adr_res = (repo / "DECISIONS.md").read_text()
    assert "<<<<<<<" not in adr_res
    assert adr_res.index("ADR-0001") < adr_res.index("ADR-0002") < adr_res.index("ADR-0003")
    assert not list(repo.glob("*.bak"))

    # Now test a real same-entry conflicting edit -> git merge must exit 1 with markers!
    git("checkout", "-b", "conflict-branch")
    (repo / "LESSONS.md").write_text(
        lessons_res.replace("From main.", "Conflict edit from branch.")
    )
    git("commit", "-am", "edit same lesson on branch")

    git("checkout", "main")
    (repo / "LESSONS.md").write_text(
        lessons_res.replace("From main.", "Conflict edit from main.")
    )
    git("commit", "-am", "edit same lesson on main")

    res_conflict = git("merge", "conflict-branch", "--no-edit", check=False)
    assert res_conflict.returncode == 1
    conflicted_text = (repo / "LESSONS.md").read_text()
    assert "<<<<<<<" in conflicted_text
    assert "=======" in conflicted_text
    assert ">>>>>>>" in conflicted_text
    assert "Conflict edit from main." in conflicted_text
    assert "Conflict edit from branch." in conflicted_text
