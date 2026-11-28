# UAT Plan: Sprint 4 — `bobp merge` for Timestamped Documents

- **Stories / criteria:** `STORY-MRG-1` (AC1–6), `STORY-MRG-2` (AC1–6), `STORY-MRG-3` (AC1–3) in [`docs/sprints/USER_STORIES_SPRINT4.md`](USER_STORIES_SPRINT4.md)
- **Environment and build:** Local checkout (`bobp 0.3.1`, Python 3.15 via `uv --locked --extra dev`, `git`, `gitleaks 8.26.0`, `dist/bobp-0.3.1-py3-none-any.whl`)
- **Date / tester:** 2026-11-28 / Trin (`*qa`)
- **Entry conditions:** Phases 1–3 implemented, unit/integration suites passing (`353 passed, 2 skipped, 218 subtests`), Switch Gates 5a cleared, Tank SDLC check passed (`test`, `lint`, `security-scan`, `build` green).
- **Exit conditions:** All in-scope acceptance criteria and negative/security paths verified PASS with reproducible evidence; zero open blocking defects.

## Scenarios

### UAT-MRG-1: CLI registration, `chat-merge` removal, `--help`, and usage errors

- **Linked criterion:** `STORY-MRG-1` AC1, AC4; `STORY-MRG-3` AC1
- **Preconditions and data:** Clean working directory / isolated `tmp_path` fixture.
- **Steps:**
  1. Run `uv run --python 3.15 --locked --extra dev bobp merge --help`
  2. Run `uv run --python 3.15 --locked --extra dev bobp chat-merge`
  3. Run `bobp merge a.md b.md` and `bobp merge --dry-run --git-driver base ours theirs`
- **Expected observable outcome:** `--help` exits `0` with `prog="bobp merge"`, supported styles, opt-in `.git/config` + `.gitattributes` `%O %A %B` snippet, exit codes `0`/`1`/`2`, and zero filesystem side effects; `chat-merge` exits non-zero as unknown subcommand; invalid flag combinations exit `2` without touching files.
- **Actual outcome:** `--help` printed full usage + opt-in snippet + exit codes and exited `0` (`HELP_OK`, zero files created); `bobp chat-merge` exited `1` (`unknown subcommand`); extra positional args and conflicting `--git-driver` flags exited `2` leaving inputs unchanged.
- **Verdict:** PASS
- **Evidence / issue:** Live CLI check + `tests/test_merge.py` (`test_cli_registers_merge_and_removes_chat_merge`, `test_help_exits_zero_with_exit_codes_and_no_side_effects`, `test_multiple_positional_files_exit_2_without_modifying_files`, `test_git_driver_rejects_conflicting_cli_flags`).

### UAT-MRG-2: Post-conflict cleanup across `CHAT.md`, `LESSONS.md`, and `DECISIONS.md` (ADRs)

- **Linked criterion:** `STORY-MRG-1` AC2, AC3, AC4
- **Preconditions and data:** Isolated fixtures covering (a) conflicted `CHAT.md` including Git-factored `---` above `<<<<<<< HEAD`, diff3 `|||||||`, exact duplicates, and date-only timestamp interpolation; (b) newest-first (`desc`) `LESSONS.md` with top-of-file conflict hunk, `---` preamble divider, and `### Context` subheadings; (c) `DECISIONS.md` / ADR log with `* **Date**:`, `- **Date:**`, and `Date:` metadata lines + `## 1. Context` subheadings; (d) live repo `agents/CHAT.md` and `docs/LESSONS.md`.
- **Steps:** Run `bobp merge <fixture>` (and `--dry-run`, `--order asc`, `--backup`), plus `uv run bobp merge --dry-run agents/CHAT.md` and `docs/LESSONS.md`.
- **Expected observable outcome:** Markers stripped, both sides preserved, exact duplicates dropped, inferred `asc`/`desc` direction respected and reported, subheadings and preamble dividers preserved, no `.bak` by default, opt-in `--backup` writes original bytes, and live repo files cleanly report `No changes needed`.
- **Actual outcome:** All 3 document styles merged cleanly in expected order; Git-factored `---` mid-file and top-of-file conflicts resolved cleanly; `--order asc` override and same-day ties preserved; live `agents/CHAT.md` (`chat, asc`) and `docs/LESSONS.md` (`heading, asc`) reported `No changes needed`.
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_merge.py` (`test_chat_*`, `test_lessons_*`, `test_adr_*`, `test_dry_run_*`, `test_clean_file_is_noop`, `test_opt_in_backup_*`) + live `--dry-run` checks.

### UAT-MRG-3: Negative & SEC-005/006/007/008/009 rejection paths

- **Linked criterion:** `STORY-MRG-1` AC5, AC6; `STORY-MRG-2` AC5, AC6
- **Preconditions and data:** Isolated fixtures with preamble conflict, missing file, non-timestamped file, invalid calendar date (`2026-02-30`), symlink target, alarm-guarded FIFO target, planted symlink/FIFO at `<path>.bak`, oversized (`>cap`) file, invalid UTF-8 binary file, ANSI/BEL escape chars in filename & date-only entry header, and 50k-char ReDoS probes (`Date:` + 50k spaces, `"a"` + 50k newlines).
- **Steps:** Execute `bobp merge` and `bobp merge --git-driver` against each hostile/invalid input.
- **Expected observable outcome:** Every hostile or invalid input is rejected cleanly with exit `1`, actionable sanitized stderr error, no blocking/hang, and zero modifications to target or victim files.
- **Actual outcome:** All rejection and security regression tests passed in `<0.7s` total; zero victim or target corruption, zero ANSI/BEL leaks, and `bobp make security-scan` passed (`gitleaks` 0 leaks, `pip-audit` clean, `npm audit` clean with accepted SEC-001).
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_merge.py` (`test_preamble_conflict_*`, `test_invalid_calendar_date_does_not_crash`, `test_missing_file_*`, `test_symlink_*`, `test_fifo_*`, `test_backup_refuses_*`, `test_oversized_*`, `test_terminal_escape_*`, `test_meta_date_regex_is_linear_time_no_redos`, `test_git_driver_sec005_*`) + Switch Gates 5a (Phases 1–3) cleared.

### UAT-MRG-4: Optional Git custom merge driver (`--git-driver`) end-to-end with real `git`

- **Linked criterion:** `STORY-MRG-2` AC1, AC2, AC3, AC4
- **Preconditions and data:** Isolated temporary Git repositories (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`) with `.gitattributes` + local `git config merge.bobp.driver` pointing to `bobp merge --git-driver %O %A %B`.
- **Steps:**
  1. Diverge two branches adding distinct entries to `CHAT.md`, `LESSONS.md` (`desc`), and `DECISIONS.md` (`ADR`) and run `git merge branch-a --no-edit`.
  2. Diverge two branches adding distinct entries to `LESSONS.md` (`desc`) and run `git rebase main`.
  3. Diverge two branches editing the same existing entry in `LESSONS.md` and run `git merge conflict-branch --no-edit`.
  4. Verify unit 3-way cases: empty base, direction fallback to `theirs`, single-side edit/delete, preamble conflict, and delete-vs-modify conflict.
- **Expected observable outcome:** Additive `git merge` and `git rebase` exit `0` automatically with chronologically ordered entries and zero `.bak` files; same-entry conflict exits `1` with valid `<<<<<<<` / `=======` / `>>>>>>>` markers preserving both versions.
- **Actual outcome:** Real `git merge` exited `0` across all 3 doc types (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`) with zero `.bak` files; real `git rebase` exited `0` (`REAL_GIT_REBASE_UAT_OK`); real same-entry `git merge` conflict exited `1` with both edits preserved inside conflict markers.
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_merge.py` (`test_git_driver_*`, `test_real_git_merge_driver_end_to_end`) + live `git rebase` UAT script run in `build/uat_rebase_*`.

### UAT-MRG-5: Active skills, packaged templates, docs, and opt-in invariant

- **Linked criterion:** `STORY-MRG-3` AC1, AC2, AC3
- **Preconditions and data:** Repository working tree after Phase 3 edits.
- **Steps:**
  1. Diff canonical vs. packaged copies (`bob-tools/SKILL.md`, `DOCUMENTATION_INDEX.md`, `SHORTHAND_GUIDE.md`).
  2. Search active code, skills, templates, and docs for stale `chat-merge` references.
  3. Run full `bobp make test`, `bobp make lint`, and `bobp make build`.
- **Expected observable outcome:** Zero canonical/packaged diffs; zero stale `chat-merge` references outside historical logs/prior sprint records; neither `install`, `update`, nor `merge` modifies `.git/config` or `.gitattributes`; all tests, Mermaid lint, and package build pass.
- **Actual outcome:** Zero diffs on all synced mirrors; `ZERO_STALE_CHAT_MERGE_REFS`; full suite `353 passed, 2 skipped, 218 subtests`, Mermaid lint PASS, wheel/sdist build PASS.
- **Verdict:** PASS
- **Evidence / issue:** `diff -u` checks, `git grep` audit, `build/build.out` from Tank Stage 3 conformance checks.

## Results and Handoff

- **Passed / failed / blocked:** 5 passed / 0 failed / 0 blocked (`UAT-MRG-1` through `UAT-MRG-5`)
- **Open issues and impact:** None.
- **Overall verdict:** PASS — all Sprint 4 acceptance criteria (`STORY-MRG-1`..`3`) and security regression cases verified against real CLI and real `git` runs with zero regressions.
- **Handoff evidence:** Ready for Smith Stage 3 end-to-end usability & UAT/LESSON rubric review (`@Smith *user test SPRINT_4`).
