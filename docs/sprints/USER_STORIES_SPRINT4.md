# Sprint 4 User Stories: `bobp merge` for Timestamped Documents

*   **Branch**: none — `docs/SDLC.md` §6 has no sprint branch; work lands on `main` and is committed only when the owner directs
*   **Source**: Owner request, 2026-11-27 (`$cypher nreq enhance chat merge tool to merge "time stamped documents"`), refined in Q&A: general timestamped Markdown logs (`CHAT.md`, lessons, decision logs, ADRs), Git conflict focus, both post-conflict cleanup and optional Git merge driver, renamed to `bobp merge` (no back-compat), Sprint 4, **KISS**
*   **Status**: Approved (Gate 1, Gate 2, Gate 2b) — Ready for Execution

## Goal

Replace `bobp chat-merge` with `bobp merge`, a small, predictable tool that resolves Git merge conflicts in timestamped Markdown documents (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`, ADR logs) by reading entry timestamps to put each entry in order (oldest-first or newest-first). Users can run `bobp merge` on an already-conflicted file or opt into it as a Git custom merge driver so `git merge` and `git rebase` resolve additive conflicts automatically.

## Assumptions made for the owner

1. **Order direction**: Infer ascending (oldest-first) vs. descending (newest-first) from the document's existing entries, defaulting to ascending when fewer than two dated entries establish an order; allow an explicit CLI override.
2. **Simple, safe conflict rule**: In post-conflict mode, distinct blocks from both sides are kept, exact duplicates are dropped, and everything is sorted — nothing is silently discarded. Conflicts inside the non-entry header/preamble are refused (file left untouched, exit `1`). In Git 3-way driver mode, additive changes merge cleanly (exit `0`), while conflicting edits to the header or to the same existing entry emit standard Git conflict markers and exit `1`.
3. **Opt-in Git driver**: `bobp install`, `bobp update`, and `bobp merge` never edit `.git/config` or `.gitattributes` automatically.
4. **No backwards compatibility**: `bobp chat-merge` is removed and replaced directly by `bobp merge`.
5. **Safe file handling (SEC-005)**: Follow `docs/LESSONS.md` — reject symlinks and special files (FIFOs) rather than following or hanging on them.

---

## STORY-MRG-1: `bobp merge` resolves conflicted timestamped Markdown documents
**Owner:** Neo

**As a** developer or persona who hits a Git conflict in `CHAT.md`, `LESSONS.md`, `DECISIONS.md`, or an ADR log,
**I want** `bobp merge [path]` to strip conflict markers, deduplicate exact duplicates, and order timestamped entries chronologically,
**so that** one simple command fixes timestamped-log conflicts across the repo instead of only `CHAT.md`.

### Acceptance Criteria
1. `bobp merge` is registered on the CLI and `bobp chat-merge` is removed (`bobp chat-merge` exits non-zero as an unknown subcommand).
2. `bobp merge [path]` (default `agents/CHAT.md`) parses and orders entries without requiring a format flag across:
   - `CHAT.md` blocks (`---` + `[<small>YYYY-MM-DD HH:MM:SS</small>]` or `[<small>YYYY-MM-DD</small>]`, keeping date-only time interpolation).
   - Date-headed sections (`## [YYYY-MM-DD] Title` or `## [YYYY-MM-DD HH:MM:SS] Title`, as in `LESSONS.md`).
   - Metadata-dated sections (`# ADR-...` / `## ...` with a leading `**Date**: YYYY-MM-DD` / `Date: YYYY-MM-DD` line, with optional `HH:MM:SS`, as in `DECISIONS.md` / ADRs).
3. Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`, `|||||||`) around timestamped entries are stripped, distinct entries from both sides are preserved, exact duplicates are dropped, the preamble before the first entry stays intact, and entries are ordered chronologically (inferred asc/desc direction, with an explicit override option; ties keep deterministic order).
4. `--dry-run` prints a concise summary of what would change without writing any file, and `--help` exits `0` with exit codes documented and zero side effects.
5. Failure/rejection: if the file is missing, is not a regular file (symlink or FIFO, per SEC-005), has no recognizable timestamped entries, or has conflict markers inside its preamble/header, `bobp merge` leaves the file untouched, prints a clear error to stderr, and exits `1`.
6. Security (`*sec`): Switch's `*sec review` of file handling (regular-file checks, no symlink following, bounded reads) has no blocking findings.

---

## STORY-MRG-2: Optional Git custom merge driver mode (`%O %A %B`)
**Owner:** Neo · **Depends on:** `STORY-MRG-1`

**As a** developer merging or rebasing branches that both add entries to a timestamped document,
**I want** `bobp merge` to work as a Git custom merge driver receiving `<base> <ours> <theirs>`,
**so that** `git merge` and `git rebase` resolve additive conflicts automatically and only stop on real same-content conflicts.

### Acceptance Criteria
1. `bobp merge` provides a Git merge-driver mode taking `<base>`, `<ours>`, and `<theirs>` (`%O %A %B`) and writes the merged result to `<ours>` (`%A`).
2. When `<ours>` and `<theirs>` add distinct timestamped entries relative to `<base>` (or make identical changes), it writes the clean chronologically ordered file to `<ours>` and exits `0`.
3. When `<ours>` and `<theirs>` make conflicting edits to the preamble or to the same existing entry relative to `<base>`, it writes standard Git conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`) preserving both versions in `<ours>` and exits `1`.
4. Verified against the real `git` binary in a temporary repo configured with `.gitattributes` and `.git/config`: `git merge` exits `0` on divergent additions in `CHAT.md`, `LESSONS.md`, and `DECISIONS.md`, and exits `1` with valid conflict markers on a same-entry edit conflict.
5. Failure/rejection: if any input path is missing, unreadable, or not a regular file (SEC-005), it prints a clear error to stderr and exits non-zero without corrupting `<ours>`.
6. Security (`*sec`): Switch's `*sec review` (no shell execution, regular-file checks, writes only to `<ours>`) has no blocking findings.

---

## STORY-MRG-3: Help text, opt-in Git setup snippet, and doc/skill updates
**Owner:** Bob & Oracle · **Depends on:** `STORY-MRG-1`, `STORY-MRG-2`

**As a** maintainer or persona using Bob Protocol,
**I want** `bobp merge --help` and active skills/docs to explain `bobp merge` and how to opt into the Git merge driver, with stale `chat-merge` references removed,
**so that** anyone can use and configure `bobp merge` cleanly without guesswork.

### Acceptance Criteria
1. `bobp merge --help` documents post-conflict mode, merge-driver mode, exit codes (`0` clean, `1` conflict/error, `2` usage), and the exact `.git/config` + `.gitattributes` snippet to opt in.
2. Active skills, packaged templates, and living docs (`bob-tools`, `chat`, `README.md`, `bobp/templates/README.md`, `SHORTHAND_GUIDE.md`, `agents/DOCUMENTATION_INDEX.md`) reference `bobp merge` with no remaining `bobp chat-merge` references outside historical chat logs/archives and Sprint 1–3 docs.
3. Neither `bobp install`, `bobp update`, nor `bobp merge` modifies `.git/config` or `.gitattributes` automatically.

---

## Out of Scope
- Backwards compatibility or alias for `bobp chat-merge`.
- Non-Markdown formats (JSON, YAML, CSV, source code).
- AI/semantic merging of conflicting edits inside the same entry.
- Automatic `.git/config` or `.gitattributes` edits during `bobp install`/`update`.
- Combining unrelated standalone files outside Git 3-way merge (`bobp chat-report --combine` covers archived chats).
- Rewriting historical records (`agents/CHAT.md`, `agents/chat_archive/`, Sprint 1–3 docs).

## Open Questions
None.

---

# Architecture: Sprint 4 — `bobp merge`

*   **Status**: Approved (Smith Gate 2, Switch Gate 2b)
*   **Author**: Morpheus
*   **Last Updated**: 2026-11-28
*   **Scope**: Sprint 4 Architecture

## 1. Executive Summary & System Overview

Replace `bobp/tools/chat_merge.py` with a single cohesive stdlib module `bobp/tools/merge.py`, registered in `bobp/cli.py` as `bobp merge` (removing `chat-merge`). One shared parser, ordering engine, and safe-file I/O layer serves both **post-conflict cleanup mode** (`bobp merge [PATH]`) and **Git custom merge driver mode** (`bobp merge --git-driver BASE OURS THEIRS`). All 6 HCI notes from Smith's Gate 1 review are incorporated into the interface contract below.

## 2. System Context & Boundaries

- **Actors**: Developers, AI personas running `bobp merge` from a shell, and Git invoking `bobp merge --git-driver %O %A %B` via `.gitattributes` + `.git/config`.
- **Filesystem boundary**: Reads and writes only the explicitly provided file path(s) (or default `agents/CHAT.md` in post-conflict mode). Never touches `.git/config`, `.gitattributes`, parent directories, or any file outside the target path.
- **Trust boundary (SEC-005)**: Input files may come from untrusted clones. Every file read/write uses `O_NOFOLLOW | O_NONBLOCK` + `fstat` `S_ISREG` verification and a read size cap (10 MiB). Zero shell execution (`subprocess` is never invoked by `merge.py`).

## 3. Component & Container Architecture

### Component Inventory

| Component | Responsibility | Inputs | Outputs |
|---|---|---|---|
| `bobp/cli.py` | Register `"merge": "bobp.tools.merge"`, remove `"chat-merge"` | CLI argv | Dispatches to `merge.main()` |
| `bobp/tools/merge.py` | Safe regular-file I/O; auto-detecting Markdown parser (`chat`, `heading`, `metadata`); conflict-marker cleaner & preamble guard; order inference & stable chronological sorter; 3-way entry/preamble merger; CLI | File path(s) + CLI flags | Merged file on disk (or dry-run summary on stdout), status/error messages, exit `0`/`1`/`2` |
| `bobp/tools/chat_report.py` | Update both relative (`from .merge`) and standalone fallback (`from merge`) imports of `BLOCK_SEP, parse_blocks` | `CHAT.md` text | Unchanged report/archive behavior |
| `bobp/tools/setup_agent_links.py` | Update legacy script message `"chat_merge.py": "bobp merge"` | Legacy `agents/tools/` | Accurate migration message |
| `tests/test_merge.py` | Unit, integration, SEC-005 hostile-file, and real-`git` merge driver tests (replaces `tests/test_chat_merge.py`) | Temp fixtures & real `git` | Pytest pass/fail |
| Docs & skills | Update active skills (`bob-tools`, `chat`, packaged mirrors) and root docs (`README.md`, `SHORTHAND_GUIDE.md`, `agents/DOCUMENTATION_INDEX.md`) | Markdown docs | Accurate `bobp merge` + opt-in Git snippet |

## 4. Runtime Interaction & Critical Flows

### Flow A — Post-Conflict Cleanup (`bobp merge [PATH]`)
1. Open `PATH` (default `agents/CHAT.md`) via `_read_regular_file` (`O_RDONLY | O_NONBLOCK | O_NOFOLLOW`, `S_ISREG`, bounded `os.read` loop ≤10 MiB, strict UTF-8 decode).
2. Inspect Git conflict hunks (`<<<<<<<`..`>>>>>>>`, with optional diff3 `|||||||`) against the document style before stripping markers:
   - A **preamble conflict** exists if a conflict hunk finishes before the first recognizable timestamped entry, OR if any non-empty branch side of a conflict hunk spanning the first entry contains non-blank non-entry text before an entry start.
   - If a conflict hunk immediately precedes the first entry and every non-empty branch side begins cleanly at an entry boundary (e.g., `---` + `[<small>...]` for `chat`, or a matching entry heading for `heading`/`metadata` — the normal newest-first / top-of-file additive conflict), it is **not** a preamble conflict and proceeds to step 3.
   - If a preamble conflict is detected → print sanitized error naming the preamble conflict to stderr, leave file untouched, exit `1`.
3. Strip conflict-marker lines (preserving both sides' content), detect document style (`chat` → `heading` → `metadata`), and split into `(preamble, entries)`. If zero timestamped entries are detected → print sanitized error to stderr, leave file untouched, exit `1`.
4. Deduplicate exact duplicate entries (first occurrence wins). For `chat` style, interpolate date-only `[<small>YYYY-MM-DD</small>]` blocks between full-timestamp neighbors and rewrite their timestamps.
5. Determine chronological direction (`asc` or `desc` via `--order auto|asc|desc`; `auto` counts increasing vs. decreasing consecutive non-inferred pairs, choosing `desc` only if strictly more decreasing pairs, else `asc`). Stable-sort entries by timestamp.
6. Reconstruct document preserving `preamble` verbatim (including any trailing `---` divider without duplicating or dropping it).
7. Compare reconstructed output with original text (sanitizing all echoed paths and entry snippets per SEC-007):
   - If `--dry-run`: print active style, direction (`asc`/`desc`), whether changes are needed (`No changes needed` vs. change counts), and exit `0`.
   - If unchanged: print clean no-op status (`No changes needed (<style>, <dir>, ...)`) and exit `0` without rewriting.
   - If changed: if `--backup` is passed, write the already-read in-memory original bytes to `<path>.bak` via `_write_regular_file` (`O_WRONLY | O_CREAT | O_NONBLOCK | O_NOFOLLOW` + `S_ISREG` + `ftruncate`; abort with exit `1` before touching `PATH` if `<path>.bak` is a symlink/FIFO/dir, ADR-S4-3); write new text safely via `_write_regular_file`; print concise summary including detected style and direction (`asc`/`desc`), and exit `0`.

### Flow B — Git Custom Merge Driver (`bobp merge --git-driver BASE OURS THEIRS`)
1. Read `BASE`, `OURS`, and `THEIRS` via `_read_regular_file` (each must exist and be a regular file, ≤10 MiB, strict UTF-8; failure exits `1` without touching `OURS`).
2. Detect style from `OURS` (fallback `THEIRS`, then `BASE`). An empty `BASE` parses as empty preamble + 0 entries. If none of the files contains recognizable timestamped entries → print error to stderr, leave `OURS` untouched, exit `1`.
3. **3-way preamble merge**: if `ours == theirs` → `ours`; else if `ours == base` → `theirs`; else if `theirs == base` → `ours`; else emit standard Git conflict markers (`<<<<<<< ours` / `=======` / `>>>>>>> theirs`) around the preamble and mark `has_conflict = True`.
4. **3-way entry merge** (keyed by normalized entry identity: header line for `chat`, normalized heading line for `heading`/`metadata`; entries sharing a key fall back to exact-body matching):
   - Unchanged on both sides → keep once.
   - Added on one side (or identically on both) → include cleanly.
   - Modified on one side, unchanged on the other → take modified version.
   - Deleted on one side, unchanged on the other → honor deletion.
   - Modified differently on both sides, deleted on one side while modified on the other, or added on both sides with the same key and different bodies → emit standard conflict markers preserving both versions at that entry's timestamp position and mark `has_conflict = True`.
5. Deduplicate exact identical entries, infer/apply order direction (`ours` → `theirs` → `base` → `asc` when `--order auto`), stable-sort entries, reconstruct document, and write to `OURS` via `_write_regular_file` (never creating `.bak`).
6. Exit `0` if `not has_conflict`, else exit `1` so Git pauses with the conflict markers in `OURS`.

## 5. Interface & Contract Specifications

* **Command**: `bobp merge [PATH] [OPTIONS]` (`ArgumentParser(prog="bobp merge", ...)`)
* **Modes** (mutually exclusive — passing both `PATH` and `--git-driver` exits `2` via `argparse`):
  * Post-conflict cleanup: `bobp merge [PATH]` (`PATH` optional, default `agents/CHAT.md`)
  * Git merge driver: `bobp merge --git-driver BASE OURS THEIRS` (explicit 3-arg flag so accidental multi-file args never overwrite the second file)
* **Options**:
  * `--order {auto,asc,desc}`: Chronological sort direction (default `auto`).
  * `--dry-run`: Preview changes in post-conflict mode without writing (rejected with exit `2` if combined with `--git-driver`).
  * `--backup`: Write a `<path>.bak` backup from in-memory original bytes using safe regular-file I/O before rewriting in post-conflict mode (default off; rejected with exit `2` with `--git-driver`).
  * `-h`, `--help`: Print usage, supported timestamp formats, opt-in `.git/config` + `.gitattributes` snippet, and exit codes; exit `0` with zero side effects.
* **Supported Document Styles** (auto-detected in priority order, line-by-line linear-time regexes using `[ \t]` instead of `\s`; invalid calendar dates like `2026-02-30` caught cleanly and treated as non-dated text):
  1. `chat`: `\n---\n` + `[<small>YYYY-MM-DD HH:MM:SS</small>]` or `[<small>YYYY-MM-DD</small>]`. Exports `BLOCK_SEP` and `parse_blocks(text)` for `bobp/tools/chat_report.py`.
  2. `heading`: Markdown ATX headings (`^#{1,6}[ \t]+`) containing an ISO date or datetime (`YYYY-MM-DD` with optional `[ T]HH:MM:SS`, optionally in brackets like `## [2026-11-01] Title`). All entries split at the heading level of the first dated heading so subheadings (`### Context`) stay inside their parent entry.
  3. `metadata`: Markdown ATX headings (`^#{1,6}[ \t]+`) at a uniform section heading level where the section's leading metadata block (lines after the heading before the first subheading or prose paragraph, up to 12 lines) contains a date field matching `^(?:[-*][ \t]+)?(?:\*\*)?Date(?:\*\*)?[ \t]*:[ \t]*(?:\*\*)?[ \t]*(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2})?)` (verified against `*   **Date**: 2026-11-27`, `- **Date:** 2026-11-27`, and `Date: 2026-11-27`).
* **Exit Codes** (documented in `--help` epilog and enforced by code):
  * `0`: Clean merge, no-op, or resolvable dry-run.
  * `1`: Unresolvable conflict (preamble conflict in cleanup mode; header or same-entry conflict in driver mode) or runtime/file error (missing file, non-regular file, no recognizable entries).
  * `2`: Invalid CLI usage (standard `argparse` error).
* **Opt-in Git Configuration Snippet** (printed in `--help`, never written automatically):
  ```ini
  # .git/config (or via: git config merge.bobp.driver "bobp merge --git-driver %O %A %B")
  [merge "bobp"]
      name = Bob Protocol timestamped Markdown merge driver
      driver = bobp merge --git-driver %O %A %B
  ```
  ```gitattributes
  # .gitattributes
  agents/CHAT.md merge=bobp
  docs/LESSONS.md merge=bobp
  docs/DECISIONS.md merge=bobp
  ```

## 6. Cross-Cutting Concepts & Resilience

### Failure Modes & Error Handling

| Failure Mode | Trigger / Condition | System Behavior | User Impact | Blast Radius |
|---|---|---|---|---|
| Missing or non-regular file | File absent, directory, symlink, or FIFO (SEC-005) | `_read_regular_file` / `_write_regular_file` rejects with `O_NOFOLLOW \| O_NONBLOCK` + `S_ISREG` | Actionable stderr error naming path, exit `1`, file untouched | None |
| Oversized / binary input | File exceeds 10 MiB read cap or fails strict UTF-8 decode | Rejected during bounded `os.read()` loop before write | Clear stderr error, exit `1`, file untouched | None |
| Unrecognized document | No timestamped entries in any supported style | Abort before write | Clear stderr error listing supported patterns, exit `1`, file untouched | None |
| Preamble conflict (cleanup) | Conflict hunk finishes before first entry or any branch side spanning first entry has non-blank non-entry text before an entry start | Abort before write | Sanitized stderr error noting preamble conflict, exit `1`, file untouched | None |
| Unsafe `.bak` target | `--backup` passed when `<path>.bak` is a symlink, FIFO, or directory | `_write_regular_file` (`O_CREAT \| O_NONBLOCK \| O_NOFOLLOW` + `S_ISREG`) aborts before modifying `PATH` | Sanitized stderr error, exit `1`, both files untouched | None |
| Same-entry / preamble conflict (driver) | Both branches modified preamble or same entry differently | Emit standard conflict markers in `OURS`, exit `1` | Git pauses with standard conflict markers for manual edit | `OURS` temp file only |
| Misused flags / extra positionals | e.g. `bobp merge a.md b.md c.md` or `--dry-run --git-driver` | `argparse` rejects before I/O | Usage error to stderr, exit `2` | None |

### Security & Privacy
* **Trust / access boundaries**: Every read/write (including `--backup` writing `<path>.bak` from already-read in-memory bytes) uses `O_NOFOLLOW | O_NONBLOCK` + `fstat` `S_ISREG` checks (`_read_regular_file` with bounded `os.read()` loop ≤10 MiB and strict UTF-8 decode; `_write_regular_file` opening `O_WRONLY | O_NONBLOCK | O_NOFOLLOW` — plus `O_CREAT` for `.bak` — verifying `S_ISREG` before `os.ftruncate(fd, 0)`, write, `fsync`, close). All echoed file paths and entry previews strip Unicode control/format chars (`category.startswith("C")`, SEC-007). No shell execution; no writes outside the explicit target (`PATH`, optional `<path>.bak`, or `OURS`).
* **Sensitive data**: Processes local project Markdown files only; no network calls, no credentials, no external transmission.

## 7. Technical Stack & SDLC / Build Impact

* **Languages & Runtime**: Python `>=3.10,<4` (local dev 3.15 via `uv`), pure Python standard library only.
* **Core Libraries & Tools**: stdlib (`argparse`, `datetime`, `os`, `re`, `stat`, `sys`, `pathlib`); `pytest` and real `git` binary in tests only.
* **Build-Environment Check (CRITICAL)**:
  * Does this design add a new language, package manager, runtime version, or external tool? **No** — no Tank Phase 0 required.
  * Routine change class under `docs/SDLC.md` §6.

## 8. Architectural Decisions (ADRs) & Technical Debt

### Decision Records

| ID | Decision | Alternatives rejected | Why |
|---|---|---|---|
| ADR-S4-1 | Single stdlib module `bobp/tools/merge.py` replacing `chat_merge.py`, retaining `BLOCK_SEP` and `parse_blocks` exports for `chat_report.py` | Multi-module plugin package; keeping dead `chat_merge.py` shim | KISS; owner confirmed no back-compat needed; `chat_report.py` stays clean with a 1-line import update |
| ADR-S4-2 | Explicit `--git-driver BASE OURS THEIRS` flag rather than overloading 3 positional arguments | `bobp merge base ours theirs` positional overload | Prevents accidental overwrite of file 2 if a user runs `bobp merge a.md b.md c.md` (Smith Gate 1 HCI #5) |
| ADR-S4-3 | No `.bak` file by default; opt-in `--backup` in cleanup mode; never in `--git-driver` mode | Always writing `.md.bak` (legacy `chat_merge.py`) | Git already tracks pre-merge state; avoids untracked `.bak` clutter in working trees (Smith Gate 1 HCI #3/#8) |
| ADR-S4-4 | Heading-level scoping for `heading` and `metadata` styles (split only at the entry heading level) | Splitting on every `#`/`##`/`###` heading | Keeps entry subheadings (`### Context`, `## 1. Context`) attached to their parent lesson/ADR entry |
| ADR-S4-5 | Exact-key 3-way merge with standard Git conflict markers on same-entry/preamble conflicts | Heuristic line-merging inside conflicting entries; last-writer-wins | Guarantees zero silent data loss while keeping the algorithm small, deterministic, and auditable |

### Acknowledged Technical Debt & Trade-offs
* Mixed-style documents (e.g., `CHAT.md` entries and `## [YYYY-MM-DD]` headings in the same file) are not supported; one document uses one style.
* Metadata-dated ADRs inside one file must use the same heading level (e.g., all `# ADR-...` or all `## ADR-...`).

