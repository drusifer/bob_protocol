# Sprint 4 Task Board: `bobp merge` for Timestamped Documents

*   **Goal**: Replace `bobp chat-merge` with `bobp merge`, a simple, conflict-safe tool for merging timestamped Markdown documents (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`, ADR logs) in both post-conflict cleanup mode and optional Git custom merge driver mode (`%O %A %B`).
*   **Tier**: Tier 1 (KISS scope) — stories and approved architecture in `docs/sprints/USER_STORIES_SPRINT4.md`
*   **Branch**: none (`docs/SDLC.md` §6 has no sprint branch; commit only when directed by owner)
*   **Status**: Complete — Sprint 4 Launched (2026-11-28)

---

## Stage 0: SDLC Gate (Blocker)

- [x] **Task 0.1:** Verify `docs/SDLC.md` exists and is current. (*Owner: Mouse | Trace: N/A — sprint gate | Verification: `test -f docs/SDLC.md`*) — verified present; pure Python stdlib change, so no Tank Phase 0 required.

---

## Sprint Execution Phases

### Phase 1: Core `bobp merge` and post-conflict cleanup
*Phase goal: Replace `bobp chat-merge` with `bobp merge` (`bobp/tools/merge.py`) supporting `chat`, `heading`, and `metadata` timestamped Markdown docs, safe post-conflict resolution with preamble guard, asc/desc ordering, `--dry-run`, opt-in `--backup`, and SEC-005/006/007 file/output safety.*
- [x] **Task 1.1:** Tests first (`tests/test_merge.py`), then replace `bobp/tools/chat_merge.py` with `bobp/tools/merge.py`, register `merge` and remove `chat-merge` in `bobp/cli.py`, update `bobp/tools/chat_report.py` (both import paths) and `bobp/tools/setup_agent_links.py`, and remove `tests/test_chat_merge.py`. (*Owner: Neo | Level: L3 — new multi-format parser, conflict-hunk guard, SEC-005/006/007 file/output safety across CLI and report integration | Trace: STORY-MRG-1, ADR-S4-1/2/3/4 | Verification: `bobp make test-q ARGS="-k 'merge or chat_report'"` then `bobp make test`*)
- [x] **Task 1.2:** UAT verification of Phase 1 acceptance criteria and security regression tests (symlink/FIFO target & `.bak`, >10 MiB, non-UTF-8, escape stripping, all 3 doc styles, asc/desc, top-of-file vs preamble conflicts). (*Owner: Trin | Level: L2 — bounded phase verification across multiple scenarios | Trace: STORY-MRG-1 AC1–5 | Verification: UAT verdict and evidence in `agents/CHAT.md`*)
- [x] **Task 1.3:** Security review of Phase 1 diff against Gate 2b threat model (verify `O_NONBLOCK | O_NOFOLLOW` + `S_ISREG` + `ftruncate`, safe in-memory `--backup`, SEC-007 sanitize, linear regex, strict UTF-8, gitleaks check). (*Owner: Switch | Level: L2 — untrusted local file I/O and terminal output | Trace: STORY-MRG-1 AC6 | Verification: `security gate (phase 1): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 1.4:** Code and architecture review (`LOOP_IMPL` rubric, ADR-S4-1..4 compliance, KISS check). (*Owner: Morpheus | Level: L2 | Trace: STORY-MRG-1, ADR-S4-1/2/3/4 | Verification: review result and `LOOP_IMPL` verdict in `agents/CHAT.md`*)

### Phase 2: Optional Git custom merge driver (`--git-driver`)
*Phase goal: Add `--git-driver BASE OURS THEIRS` 3-way merging for timestamped documents and verify end-to-end with the real `git` binary.*
- [x] **Task 2.1:** Tests first (3-way unit tests, SEC-005 hostile-file driver tests, and isolated real-`git` E2E merge tests using `GIT_CONFIG_GLOBAL=/dev/null` across `CHAT.md`, `LESSONS.md`, `DECISIONS.md` plus same-entry/preamble conflict cases), then implement `--git-driver` 3-way merge in `bobp/tools/merge.py`. (*Owner: Neo | Level: L3 — 3-way entry/preamble merge state machine + real Git integration | Trace: STORY-MRG-2, ADR-S4-2/5 | Verification: `bobp make test-q ARGS="-k merge"` then `bobp make test`*)
- [x] **Task 2.2:** UAT verification of `--git-driver` with real `git merge` and `git rebase` scenarios (additive clean exit `0`, conflicting same-entry & preamble exit `1` with valid markers, invalid/non-regular inputs). (*Owner: Trin | Level: L2 — multi-scenario Git integration UAT | Trace: STORY-MRG-2 AC1–5 | Verification: UAT verdict and evidence in `agents/CHAT.md`*)
- [x] **Task 2.3:** Security review of Phase 2 diff (zero shell execution, regular-file checks on all 3 inputs, writes strictly limited to `OURS`, never creates `.bak`). (*Owner: Switch | Level: L2 — Git driver boundary | Trace: STORY-MRG-2 AC6 | Verification: `security gate (phase 2): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 2.4:** Code and architecture review (`LOOP_IMPL` rubric, ADR-S4-5 compliance). (*Owner: Morpheus | Level: L2 | Trace: STORY-MRG-2, ADR-S4-5 | Verification: review result and `LOOP_IMPL` verdict in `agents/CHAT.md`*)

### Phase 3: Help snippet, skills, and documentation updates
*Phase goal: Finalize `bobp merge --help` opt-in Git snippet and update all active skills, packaged templates, and living docs to `bobp merge` with zero stale `chat-merge` references.*
- [x] **Task 3.1:** Verify/polish `bobp merge --help` opt-in `.git/config` + `.gitattributes` snippet and exit-code epilog; update active skills + packaged template mirrors (`bob-tools`, `chat`, `bobp/templates/README.md`) and living repo docs (`README.md`, `SHORTHAND_GUIDE.md`, `agents/DOCUMENTATION_INDEX.md`); confirm `bobp install`/`update`/`merge` never auto-modify `.git/config` or `.gitattributes`. (*Owner: Bob & Oracle | Level: L2 — coordinated doc/skill sync across canonical and packaged copies | Trace: STORY-MRG-3 AC1–3 | Verification: `git grep "chat-merge"` clean in active docs/skills and `bobp make test` passes*)
- [x] **Task 3.2:** Verify help output, doc/template parity tests, and confirm no stale `chat-merge` references remain in active docs/skills. (*Owner: Trin | Level: L1 — bounded verification | Trace: STORY-MRG-3 AC1–3 | Verification: `bobp make test` and grep evidence in `agents/CHAT.md`*)
- [x] **Task 3.3:** Security review quick pass (text/docs only; confirm opt-in Git snippet uses only `%O %A %B` and no auto-config mutation). (*Owner: Switch | Level: L1 — text-only quick pass | Trace: STORY-MRG-3 AC3 | Verification: `security gate (phase 3): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 3.4:** Final phase review confirming doc accuracy and parity. (*Owner: Morpheus | Level: L1 | Trace: STORY-MRG-3 | Verification: review result in `agents/CHAT.md`*)

---

## Stage 3: Sprint Closeout

- [x] **Task C.1:** SDLC conformance check (clean rebuild & security-scan/test/lint checks per `docs/SDLC.md`). (*Owner: Tank | Level: L2 — clean rebuild & conformance check | Trace: N/A — closeout | Verification: `bobp make test`, `bobp make lint`, `bobp make security-scan`, and SDLC verification note in `agents/CHAT.md`*)
- [x] **Task C.2:** Document grooming, lesson review, and Sprint 4 chat report (`bobp chat-report --moniker SPRINT_4`). (*Owner: Oracle | Level: L1 — bounded doc closeout | Trace: N/A — closeout | Verification: `bobp chat-report --moniker SPRINT_4 --summary "..."`*)
- [x] **Task C.3:** End-to-end user usability testing against `docs/sprints/UAT_PLAN_SPRINT4.md` (UAT rubric + HCI heuristics). (*Owner: Smith | Level: L2 — end-to-end CLI & Git usability testing | Trace: STORY-MRG-1 to STORY-MRG-3 | Verification: Smith acceptance verdict and `rubric UAT` line in `agents/CHAT.md`*)
- [x] **Task C.4:** Sprint retrospective & backlog grooming (all personas post retros to Cypher). (*Owner: Mouse | Level: L1 — closeout coordination | Trace: N/A — closeout | Verification: retros posted in `agents/CHAT.md`*)
- [x] **Task C.5:** Sprint 4 launch & release decision announcement (commits/releases remain owner's decision per SDLC §6/§7). (*Owner: Cypher | Level: L1 — closeout announcement | Trace: N/A — release decision | Verification: `*pm launch SPRINT_4` in `agents/CHAT.md`*)
