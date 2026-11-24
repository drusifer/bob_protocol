# UAT Plan: Sprint 2 — Version-Aware bobp

- **Stories / criteria:** STORY-BOBP-1 to STORY-BOBP-4 in `docs/sprints/USER_STORIES_SPRINT2.md`
- **Environment and build:** bobp 0.2.0 from the working tree on top of `ee7ce0e` (uncommitted Sprint 2 changes), run through the real CLI (`uv run bobp ...`) in throwaway projects under the session scratchpad; `CODEX_HOME` redirected so no global state is touched
- **Date / tester:** 2026-11-01 / Smith (with Trin's phase UATs, recorded in `agents/CHAT.md`)
- **Entry conditions:** full suite green (166 passed), SEC-005 fixed, Switch phase 2 gate clear
- **Exit conditions:** every acceptance criterion passes on the real CLI; unresolved issues listed below

## Scenarios

### UAT-1: Ask for the version anywhere

- **Linked criterion:** STORY-BOBP-1 AC1–5
- **Preconditions and data:** an empty directory outside any project; also a project whose stamp is stale
- **Steps:** `bobp --version`; `bobp -V`; `bobp --help`; repeat `--version` inside the stale project
- **Expected observable outcome:** `bobp 0.2.0`, exit 0, nothing written, no notice, help lists `-V, --version`
- **Actual outcome:** as expected; the directory stayed empty and the stale project printed no notice
- **Verdict:** PASS
- **Evidence / issue:** Trin phase 1 UAT; Smith re-run in the stale project

### UAT-2: A new project records the version

- **Linked criterion:** STORY-BOBP-2 AC1, AC2, AC4
- **Preconditions and data:** empty project directory whose name contains a space
- **Steps:** `bobp install "My Project"`; read `agents/.bobp-version`; later `bobp update` after resetting the stamp to `old`
- **Expected observable outcome:** one-line file `0.2.0`; update rewrites it; state and chat files are untouched
- **Actual outcome:** stamp `0.2.0` after install and after update; `agents/neo/state.md` contents preserved
- **Verdict:** PASS
- **Evidence / issue:** Trin phase 1 UAT

### UAT-3: Failed install leaves the stamp alone

- **Linked criterion:** STORY-BOBP-2 AC3
- **Preconditions and data:** project with an existing `agents/` and stamp `old`
- **Steps:** `bobp install <project>` without `--force`
- **Expected observable outcome:** refuses with exit 1; stamp still `old`
- **Actual outcome:** exit 1, stamp `old`
- **Verdict:** PASS
- **Evidence / issue:** Trin phase 1 UAT

### UAT-4: A stale project tells the user what to do, then carries on

- **Linked criterion:** STORY-BOBP-3 AC1–4, STORY-BOBP-4 AC1
- **Preconditions and data:** installed project, stamp edited to `0.1.0`, command run from a nested directory
- **Steps:** `bobp chat "stale project" ...`; run again; paste the printed command; run `bobp chat` again
- **Expected observable outcome:** the chat message is still posted; exactly one stderr line names `bobp 0.1.0`, `bobp 0.2.0` and a quoted `bobp update '<path>'`; the line repeats on the second run; the pasted command updates the project; afterwards stderr is empty
- **Actual outcome:** all of the above; the pasted command (path with a space) worked and the stamp became `0.2.0`
- **Verdict:** PASS
- **Evidence / issue:** this session's end-to-end run, steps [2]–[6]

### UAT-5: Missing, unreadable, newer and disabled

- **Linked criterion:** STORY-BOBP-3 AC2, AC5, AC6; STORY-BOBP-4 AC2–4
- **Preconditions and data:** project with no stamp; stamp `junk`; stamp `0.10.0`; stamp equal; `BOBP_NO_VERSION_CHECK=1`; a directory outside any project
- **Steps:** run a subcommand in each state; compare stdout and exit code with the no-check baseline
- **Expected observable outcome:** missing/junk: one line saying "unrecorded bobp version"; `0.10.0`, equal, env switch, outside a project: silent; stdout (21 lines for the probe command) and exit code 0 identical in every state
- **Actual outcome:** matched, including `0.10.0` correctly treated as newer than `0.2.0`
- **Verdict:** PASS
- **Evidence / issue:** Trin phase 2 UAT; end-to-end run steps [7]–[8]

### UAT-6: A hostile stamp cannot hang or garble the terminal

- **Linked criterion:** STORY-BOBP-4 AC3, AC4 (SEC-005)
- **Preconditions and data:** stamp as a symlink to `/dev/stdin` with an open pipe on stdin; stamp as a FIFO; stamp containing an ESC sequence
- **Steps:** run a subcommand with a 4-second timeout
- **Expected observable outcome:** returns promptly with exit 0 and the "unrecorded" notice; no raw ESC byte on stderr
- **Actual outcome:** before the fix exit 124 (hung); after the fix exit 0 with the notice; no ESC byte
- **Verdict:** PASS
- **Evidence / issue:** SEC-005 (`agents/switch/findings/2026-11-01-version-stamp-symlink-hang.md`)

## Results and Handoff

- **Passed / failed / blocked:** 6 / 0 / 0 (UAT-1 to UAT-6)
- **Open issues and impact:** (a) This repository's own `agents/` has no stamp, so every bobp command run here prints the notice; resolving it means running `bobp update .` on the live personas, a decision for the owner. (b) `bobp make distclean` crashes the wrapper after cleaning (logged in SDLC §9, pre-existing).
- **Overall verdict:** PASS
- **Handoff evidence:** Smith acceptance posted in `agents/CHAT.md`
