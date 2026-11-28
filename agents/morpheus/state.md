# Agent State

## Context
- 2026-11-28: Authored Sprint 4 Architecture in `docs/sprints/USER_STORIES_SPRINT4.md` for `bobp merge` (replacing `bobp chat-merge`, no back-compat, KISS).
- Key ADRs: ADR-S4-1 (single stdlib `bobp/tools/merge.py` exporting `BLOCK_SEP`/`parse_blocks` for `chat_report.py`), ADR-S4-2 (explicit `--git-driver BASE OURS THEIRS` flag), ADR-S4-3 (no `.bak` by default, opt-in `--backup`, never in driver mode), ADR-S4-4 (heading-level scoping for `heading`/`metadata` styles), ADR-S4-5 (exact-key 3-way merge emitting standard conflict markers on same-entry/preamble conflicts).
- Incorporated all 6 Smith Gate 1 HCI notes and SEC-005 regular-file I/O (`O_NOFOLLOW | O_NONBLOCK`, `fstat` `S_ISREG`, 10 MiB cap, `ftruncate` after `fstat`).
- Build-environment check: No new language, dependency, runtime, or Make target — no Tank Phase 0 needed.

## Current Task
**Status:** Sprint 5 Architecture (`ADR-S5-1..4`), Phase 1–2 code reviews (`APPROVE`), and evaluation tradeoffs complete; Sprint 5 LAUNCHED (2026-11-28).
**Assigned to:** Morpheus (`*lead`) — complete
**Progress:** Approved Sprint 3 Phases 5, 6, and 7 (`rubric LOOP_IMPL: TFIRST=A VERIF=S MODUL=S REGRESS=S BUDGET=S`; caught and verified fix for legacy `.agents -> agents` symlink crash in `update --dry-run` plus `bob-tools/SKILL.md` cleanup). Sprint 4 also launched.

## Next Steps
1. Await user direction for next sprint or release review.
2. Address minor Sprint 3/4 retro backlog items when scheduled.
