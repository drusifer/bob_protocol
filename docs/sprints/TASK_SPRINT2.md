# Sprint 2 Task Board: Version-Aware bobp

*   **Goal**: `bobp --version` reports the installed version, and `install`/`update` record that version in each project. Running bobp in a project whose recorded version is missing or older prints the `bobp update` instruction to stderr and continues the command, with no prompt.
*   **Tier**: Tier 2 (Minor/Fast-track) — stories and architecture are combined in `docs/sprints/USER_STORIES_SPRINT2.md`
*   **Branch**: none (the SDLC defines no sprint branch; commit only when the user directs)
*   **Status**: Complete — all gates passed, launched 2026-11-01 (uncommitted; release and version bump are the owner's call). One fix loop: SEC-005.

---

## Stage 0: SDLC Gate (Blocker)

- [x] **Task 0.1:** Verify `docs/SDLC.md` exists and is current. (*Owner: Mouse | Trace: N/A — sprint gate | Verification: `test -f docs/SDLC.md`*) — present, last verified 2026-10-30. No build-environment change in the design, so there is no Phase 0.

---

## Sprint Execution Phases

### Phase 1: `--version` and the version stamp
*Phase goal: `bobp --version` works anywhere, and `install`/`update` write `agents/.bobp-version`.*
- [x] **Task 1.1:** Tests first, then add `-V/--version` and a `--version` line in help to `bobp/cli.py`; add `STAMP_NAME` and a stamp write as the last step of `install()` and `update()` in `bobp/tools/_bob_manage.py`; stamp must not be written if either exits early. (*Owner: Neo | Level: L2 — a few connected edits in two files, clear acceptance, established patterns | Trace: STORY-BOBP-1, STORY-BOBP-2 | Verification: `bobp make test-q ARGS="-k 'version or stamp'"` then `bobp make test`*)
- [x] **Task 1.2:** UAT of Phase 1: `bobp --version` and `-V` outside any project; `bobp --help` lists the flag; fresh `bobp install` and `bobp update` into temp dirs produce the one-line stamp and leave state files untouched; a failed install leaves no stamp. (*Owner: Trin | Level: L1 — one clear check set | Trace: STORY-BOBP-1 AC1–5, STORY-BOBP-2 AC1–4 | Verification: UAT verdict and evidence in `agents/CHAT.md`*)
- [x] **Task 1.3:** Security review of the Phase 1 diff against the design threat model (stamp contents untrusted; file write location). (*Owner: Switch | Level: L1 — small diff, known checklist | Trace: security design gate / N/A — quick pass expected | Verification: `security gate (phase 1): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 1.4:** Code review and ADR-S2-1/ADR-S2-2 compliance check. (*Owner: Morpheus | Level: L1 — review of a bounded diff | Trace: STORY-BOBP-1, STORY-BOBP-2, ADR-S2-1 | Verification: review result recorded in `agents/CHAT.md`*)

### Phase 2: The version check and its safeguards
*Phase goal: a stale or unstamped project gets a one-line update notice on stderr; the subcommand always still runs unchanged.*
- [x] **Task 2.1:** Tests first, then create `bobp/tools/_version_check.py` (find project, read and parse stamp, leading-integer compare, sanitized stderr notice (control characters stripped from stamp text and path; path `shlex.quote`d), `BOBP_NO_VERSION_CHECK`, catch-all so failures never block); add `find_project_root_or_none()` to `_common.py`; call the check from `cli.main()` for every subcommand except `install` and `update`. (*Owner: Neo | Level: L3 — cross-cutting behavior at the dispatcher, untrusted input, and failure handling across components | Trace: STORY-BOBP-3, STORY-BOBP-4, ADR-S2-2 to ADR-S2-5 | Verification: `bobp make test-q ARGS="-k version_check"` then `bobp make test`*)
- [x] **Task 2.2:** UAT of Phase 2, in a temp project at each state: missing stamp, older stamp, equal, newer, garbage, unreadable. For missing, older and garbage stamps confirm exactly one stderr line naming both versions and `bobp update <project>`, nothing extra on stdout, no stdin read, and the command's output and exit code unchanged; for equal and newer stamps confirm silence; confirm the line repeats each run until `bobp update` stamps the project, and that `BOBP_NO_VERSION_CHECK=1` suppresses it. (*Owner: Trin | Level: L2 — several scenarios within one feature | Trace: STORY-BOBP-3 AC1–6, STORY-BOBP-4 AC1–4 | Verification: UAT verdict and evidence in `agents/CHAT.md`*)
- [x] **Task 2.3:** Security review of the Phase 2 diff: no stamp contents reach a shell, path or format string; control characters stripped from echoed text; the path shown is the discovered root; the check is read-only and never reads stdin. (*Owner: Switch | Level: L2 — untrusted input echoed to terminal output | Trace: security design gate | Verification: `security gate (phase 2): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 2.4:** Code review and ADR compliance check, including confirmation that no new dependency or make target was added. (*Owner: Morpheus | Level: L2 — review across the dispatcher, helper and tests | Trace: STORY-BOBP-3, STORY-BOBP-4, ADR-S2-2 to ADR-S2-5 | Verification: review result recorded in `agents/CHAT.md`*)

---

## Stage 3: Sprint Closeout

- [x] **Task C.1:** SDLC conformance check, plus propose the one-sentence SDLC §7 addition about `agents/.bobp-version`. (*Owner: Tank | Level: L2 — clean rebuild plus a small doc change | Trace: N/A — closeout | Verification: `bobp make distclean && bobp make install && bobp make test`*)
- [x] **Task C.2:** Document grooming (mention `--version` and the update notice where bobp's commands are documented), lesson archiving, and chat report. (*Owner: Oracle | Level: L1 — bounded documentation work | Trace: N/A — closeout | Verification: `bobp chat-report --moniker SPRINT_2 --summary "bobp gained --version, a per-project version stamp, and an update notice for stale projects."`*)
- [x] **Task C.3:** End-to-end usability testing of the notice wording and flow, and lesson review. (*Owner: Smith | Level: L2 — multiple user-facing scenarios | Trace: STORY-BOBP-1 to STORY-BOBP-4 | Verification: Smith acceptance verdict and evidence recorded in `agents/CHAT.md`*)
- [x] **Task C.4:** Sprint retrospective and backlog grooming. (*Owner: Mouse | Level: L1 — bounded facilitation | Trace: N/A — closeout | Verification: retros posted in `agents/CHAT.md`*)
- [x] **Task C.5:** Sprint launch and release announcement (the version bump and release remain a separate user decision per SDLC §6/§7). (*Owner: Cypher | Level: L1 — one decision and announcement | Trace: N/A — release decision | Verification: Cypher launch decision recorded in `agents/CHAT.md`*)
