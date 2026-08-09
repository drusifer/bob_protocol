# Sprint SPRINT_1 — Chat Archive & Report

Scoped from a direct user request (routed through Bob → `/sprint`), refined
via live clarifications mid-conversation.

## Context

Sprint close currently has no repeatable way to archive `CHAT.md` — Oracle's
`*ora archive` moves the top 75% by hand into a date-stamped file. We want a
Python-owned, sprint-moniker-based archive step, plus two smaller fixes to
existing chat tooling that came up during scoping.

## Stories

### S1 — Sprint-close chat archive (`bobp chat-report`)
**As** a persona closing out a sprint (Oracle, per the sprint-close step),
**I want** a single command that archives `CHAT.md` and `CHAT.diagram.md`
under the sprint's moniker,
**so that** CHAT.md can reset for the next sprint without losing history.

Acceptance criteria:
- New subcommand `bobp chat-report --moniker <MONIKER> --summary <TEXT>` (or `--summary-file <PATH>`).
- All file I/O (read CHAT.md, read CHAT.diagram.md, write archive files, reset CHAT.md) lives in Python. The calling persona supplies only the summary text — no file paths, no manual copying.
- Writes `agents/chat_archive/CHAT_<MONIKER>.md` and `agents/chat_archive/CHAT_<MONIKER>.diagram.md`, each prefixed with a heading built from the supplied summary.
- After archiving, `CHAT.md` is reset to a short header pointing at the new archive file (so continuity isn't lost), and `CHAT.diagram.md` is regenerated to match (effectively empty until the next post).
- Errors clearly if the moniker's archive files already exist (no silent overwrite) unless `--force` is passed.

### S2 — Combine archives (`bobp chat-report --combine`)
**As** Oracle or a human reviewing project history,
**I want** one command that stitches every archived sprint back into a single file,
**so that** I can read the full project conversation history in one place.

Acceptance criteria:
- `bobp chat-report --combine` reads every `agents/chat_archive/CHAT_<MONIKER>.md` (and its `.diagram.md` twin), in chronological/moniker order, and writes `agents/chat_archive/CHAT_FULL.md` and `agents/chat_archive/CHAT_FULL.diagram.md`.
- Each sprint's section in the combined file is headed by that sprint's summary (extracted from the archive's own heading — not re-supplied).
- Re-running `--combine` after a new archive is added regenerates `CHAT_FULL.*` from scratch (idempotent, not additive).

### S3 — Word-wrap diagram labels
**As** anyone reading `CHAT.diagram.md`,
**I want** message labels wrapped to a readable width instead of truncated at 100 characters with `…`,
**so that** I can see the full message content in the rendered Mermaid diagram.

Acceptance criteria:
- `chat_diagram.py`'s label rendering wraps long messages across multiple lines (Mermaid `<br/>`) at a reasonable width instead of cutting them off.
- A sane upper bound still exists so one giant message can't blow up the diagram (cap total lines/length, ellipsis only past that cap).

### S4 — `chat-merge` strips conflict markers
**As** a persona resolving a git merge conflict in `CHAT.md`,
**I want** `bobp chat-merge` to strip leftover `<<<<<<<`/`=======`/`>>>>>>>`/`|||||||` conflict-marker lines and drop exact-duplicate blocks,
**so that** a conflicted `CHAT.md` comes out clean without hand-editing.

Acceptance criteria:
- Conflict-marker lines are stripped before block parsing; content from both sides of the conflict is preserved (not discarded).
- Exact-duplicate blocks (identical content, e.g. both branches appended the same entry) are deduped after sorting.
- Existing timestamp-interpolation/sort behavior is unchanged for conflict-free input.

## Out of scope
- Changing the existing `*ora archive` (75%-rolling, date-stamped) behavior — S1 is a distinct, sprint-moniker-based full archive, not a replacement.
- Any UI/rendering beyond Mermaid label wrapping.
