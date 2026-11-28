# Agent State

## Context
- 2026-11-28: Sprint 4 Phase 1 passed all gates (Trin UAT, Switch Gate 5a after fixing SEC-008 & SEC-009, Morpheus `APPROVE`).
- 2026-11-28: Sprint 4 Phase 2 implemented via TDD (`tests/test_merge.py` RED → GREEN):
  - Implemented `merge_git_driver(base_path, ours_path, theirs_path, order="auto")` in `bobp/tools/merge.py` (`--git-driver BASE OURS THEIRS`).
  - 3-way preamble merge, 3-way entry merge keyed by entry identity with duplicate-key fallback, direction fallback (`ours -> theirs -> base -> asc`), conflict markers (`<<<<<<< ours` / `=======` / `>>>>>>> theirs`) + exit `1` on preamble/same-entry/delete-vs-modify conflicts, SEC-005 regular-file I/O on all 3 paths, writes strictly to `OURS`, never creates `.bak`.
  - Added unit, SEC-005 hostile-input, and isolated real-`git` E2E merge tests (`GIT_CONFIG_GLOBAL=/dev/null`, `shell=False`) across `CHAT.md`, `LESSONS.md`, and `DECISIONS.md`.
  - Full suite passed: `353 passed, 2 skipped, 218 subtests passed`.

## Current Task
**Status:** Sprint 3 Phase 7 implementation complete (fixed legacy `.agents` symlink `--dry-run` preview + SEC-007 `printable()` polish + `--help` version-check bypass test + `bob-tools` skill sync).
**Assigned to:** Morpheus (`*lead review phase-7` re-check)
**Progress:** Task 7.1 complete across all 17 subcommands (`cli.py`, `_bob_manage.py`, `bob_*.py`, `make.py`, `tldr.py`, `setup_agent_links.py`, `prep_tldr.py`, `tests/test_cli_help.py`).

## Next Steps
1. Await Morpheus Phase 7 re-review approval.
2. Advance to Sprint 3 Stage 3 Closeout (Tank SDLC update/check, Oracle groom + chat-report, Smith E2E UAT, Team Retro, Cypher Launch).
