# SPRINT_1 Architecture — Chat Archive & Report

## S1/S2 — `bobp/tools/chat_report.py` (new module, new `chat-report` subcommand)

Reuses `parse_blocks`/`BLOCK_SEP` already defined in `chat_merge.py` (imported,
not duplicated) to split `CHAT.md` into `(header, blocks)`.

### `archive(chat_file, diagram_file, archive_dir, moniker, summary, force=False)`
1. Read `chat_file`; `header, blocks = parse_blocks(text)`. Error if no blocks ("nothing to archive").
2. Target paths: `archive_dir/CHAT_<MONIKER>.md`, `archive_dir/CHAT_<MONIKER>.diagram.md`. Error if either exists, unless `--force`.
3. Write the `.md` archive: `# CHAT_<MONIKER> — Sprint Archive` heading, `## Summary` section with the supplied summary, `---`, then the original blocks joined by `BLOCK_SEP`. The message-template preamble (the "how to post" header) is **not** duplicated into the archive — it's static instructions, not history.
4. Write the `.diagram.md` archive: take the current `diagram_file` content, replace its leading boilerplate header (everything before the ` ```mermaid ` fence) with the same `# CHAT_<MONIKER> —  Sprint Archive` + `## Summary` heading, keep the fenced Mermaid block as-is.
5. Reset `chat_file`: keep the original `header` (message-template preamble) verbatim, append a pointer line — `> **Previous sprint archived:** \`agents/chat_archive/CHAT_<MONIKER>.md\` — <first line of summary>` — then an empty `---` ready for the next post.
6. Regenerate `diagram_file` from the now-empty chat via the existing `chat_diagram.regenerate()` so both files stay in sync.
7. Return the two archive paths (printed by `main()`).

All file I/O — reads, writes, path construction, existence checks — lives here in Python. The calling persona's only input is `--moniker` and `--summary`/`--summary-file` text.

### `combine(archive_dir, out_md, out_diagram)`
1. Glob `archive_dir` for `CHAT_*.md`, split into content archives vs `*.diagram.md` archives (by suffix, since the diagram glob is a subset of the `.md` glob). Excludes any pre-existing `CHAT_FULL.md`/`CHAT_FULL.diagram.md` from the input set.
2. Sort by moniker using a natural-sort key (splits trailing digits so `SPRINT_2` sorts before `SPRINT_10`) rather than plain lexicographic sort.
3. Each archive file already carries its own `## Summary` heading (written by `archive()`), so `combine()` just concatenates the full file contents in order — it does not need to be handed summaries again — under a `# CHAT_FULL — Combined Sprint History` top banner, joined by `---`.
4. Same approach for the diagram archives → `CHAT_FULL.diagram.md`.
5. Always regenerates both files from scratch (idempotent — safe to re-run after adding a new archive).

### CLI (`main()`)
```
bobp chat-report --moniker SPRINT_1 --summary "..."      # archive mode
bobp chat-report --moniker SPRINT_1 --summary-file f.md  # archive mode, long summary
bobp chat-report --combine                                # combine mode
```
`--combine` is mutually exclusive with `--moniker`/`--summary`/`--summary-file`. `--force` skips the overwrite guard in archive mode. `--chat-file`/`--diagram-file`/`--archive-dir` default via `find_project_root()` like the other tools. Register in `cli.py`'s `SUBCOMMANDS` as `"chat-report": "bobp.tools.chat_report"`.

Archive directory: `agents/chat_archive/` (already an established convention — used by the existing manual `*ora archive` step).

## S3 — `chat_diagram.py` word-wrap

Replace the current hard-truncate (`_clean_message`, 100-char cutoff + `…`) with:
- Raise the *cap* (full-message safety limit) to ~300 chars, ellipsis only past that.
- `textwrap.wrap()` the (capped) message at ~40 chars/line, join lines with `<br/>` — Mermaid sequence-diagram message text supports inline `<br/>` for line breaks.
- Applies inside `_label_for()`, which already composes `f"{cmd} — {snippet}"`; the cmd prefix stays on the first line, only the snippet wraps.

## S4 — `chat_merge.py` conflict-marker stripping + dedup

Two additions to the existing timestamp-interpolation flow, no change to current behavior on conflict-free input:

1. `strip_conflict_markers(text) -> (clean_text, count)`: regex-strips `^<{7} .*$`, `^\|{7} .*$` (diff3 common-ancestor), `^={7}$`, `^>{7} .*$` line-anchored markers (exact 7-char run, so we don't accidentally eat a `=======` that's part of real message content unless it's a bare 7-`=` line). Collapses the blank-line runs left behind. Both sides' actual content survive — they just become plain sequential blocks, which the existing timestamp-sort already reconciles correctly.
2. `dedup_blocks(blocks) -> (deduped, dupe_count)`: drops blocks whose stripped text exactly duplicates an earlier block (common outcome of a bad conflict resolution where the same entry lands on both sides). Runs right after `parse_blocks()`, before interpolation.

`merge()` calls both, and both dry-run and real-write output report `N markers stripped, M duplicates removed` alongside the existing block/inferred/reordered counts.

## Open items for Mouse to phase
- Phase 1: `chat_report.py` (archive + combine) + `cli.py` registration + tests.
- Phase 2: `chat_diagram.py` word-wrap + tests.
- Phase 3: `chat_merge.py` conflict-marker + dedup + tests.
- Phase 4: wire the archive step into `agents/skills/sprint/SKILL.md` Stage 3 Step 7 (Oracle groom) and `agents/oracle.docs/SKILL.md` `*ora archive` section — Oracle's sprint-close groom step now calls `bobp chat-report --moniker <SPRINT> --summary "<oracle's summary>"` instead of hand-moving text.

No new external dependencies. No breaking changes to `chat-merge`'s existing CLI surface (`--file`, `--dry-run` unchanged).
