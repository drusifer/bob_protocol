# Agent State

## Context
### Recent Decisions
- User decided: drop bob-owned Makefile management from `bobp install`/`update` entirely — the
  host project's `Makefile` is now 100% its own, untouched by bob. `bobp` only wraps whatever
  `make <target>` the host already defines, via a renamed `bobp make` subcommand (was `bobp mkf`).
- User explicitly kept bob_protocol's own root `Makefile` (install/test/build/clean for building
  the bobp package itself) — that one was NOT touched, per direct instruction mid-task.
- Accepted tradeoff: bare `make <target>` in a project now runs uncaptured/unposted straight to
  the terminal. There is no more auto-intercept safety net for agents who forget `bobp make`.
  The `make` skill's "NEVER bare `make`" rule is now the only thing enforcing capture.

### Key Findings
- `bobp mkf` (now `bobp make`) never actually needed the `MKF_ACTIVE` env var for its own
  capture logic — that var was only consumed by the *installed* Makefile's own
  `ifdef MKF_ACTIVE` / `Makefile.prj` / `Makefile.bob` self-re-inclusion dance. Once that dance
  is deleted, `bobp make <target>` still works unchanged: it just shells out to `make <target>`
  and captures stdout/stderr — no coupling to the target Makefile's internals at all.
- Found bob_protocol's own dev-environment gap (pre-existing, unrelated to this task): the
  system `python`/`pytest` on this machine has no `bobp` installed, only the pipx venv at
  `/home/drusifer/.local/share/pipx/venvs/bobp/bin/python` does (editable, pointing at this
  repo). Use that interpreter for an accurate `pytest tests/ -q` run in this repo until the
  system env is fixed — confirmed via `git stash` that this is not something my changes caused.
- `agents/skills/bob-tools/SKILL.md` (and neo.docs/SKILL.md's own Make Rules block) were stale
  in a second, unrelated way: they still described `agents/tools/*.py` as project-local scripts
  and `python agents/tools/setup_agent_links.py` invocations, from before bobp was packaged as
  a CLI (commit 4523a99). Rewrote both to the current `bobp <subcommand>` reality while in there
  for the make cleanup — same root confusion, adjacent cause.

### Follow-up fixes (same session, user-directed)
- User caught two real bugs while reviewing the test failure I'd called "pre-existing/
  environment-only": (1) `tests/test_chat_diagram.py`'s `ChatPyIntegrationTests` shelled out via
  `subprocess.run([sys.executable, "-m", "bobp.tools.chat", ...], cwd=tmp)` — the *actual* root
  cause wasn't "system python lacks bobp", it was that `cwd=tmp` broke the accidental
  cwd-added-to-sys.path trick that let `bobp` import at all in this not-really-installed dev
  checkout. User's instinct ("it's a python module, we can just use it") was right — rewrote the
  test to call `chat.main()` in-process (`os.chdir` + `patch("sys.argv", ...)`) instead of
  spawning a subprocess. Now passes under plain `python3 -m pytest`, no venv workaround needed.
  Root Makefile's `install`/`test`/`build` now depend on a `$(VENV_STAMP)` file
  (`.venv/.install.stamp`, keyed on `pyproject.toml`) and run everything through
  `.venv/bin/python` — never bare `pip`/`pytest`/`python` off PATH. Verified: fresh `make test`
  creates `.venv` and installs, a second run skips reinstall (stamp works), `make build` and
  `bobp make test` (the full wrapped path) both work end-to-end.

### Important Notes
- Left `agents/skills/render/SKILL.md`'s many generic `make deploy`/`make logs`/etc. mentions
  mostly as-is beyond the one clearly-broken `Makefile.prj`/mkf-stub line — deciding which of
  those should become `bobp make X` (captured) vs. stay bare `make X` (streaming/interactive,
  e.g. `make logs`) is a judgment call belonging to whoever owns that project-specific skill,
  not a mechanical rename. Flagged here in case Morpheus/Tank want to revisit.
- `agents/skills/judge/SKILL.md`'s `make judge-trace` / `trace_annotate.py` invocation model
  has its own pre-existing packaging staleness (same `agents/tools/*.py` vs `bobp <subcommand>`
  issue) that I did NOT fully fix — only touched the one line that directly referenced
  "mkf-captured". Worth a dedicated pass if judge-trace is actually run as documented.

## Current Task
**Status:** Complete, tested, not yet committed
**Assigned to:** Neo
**Started:** 2026-08-06

### Task Description
Drop bob's ownership of installed-project Makefiles ("give the Makefile back to the host
project") and make `bobp make <target>` the supported way to run project make targets with
output capture (`build/build.out`) + CHAT.md status posting. Root `Makefile` for bob_protocol
itself stays untouched per explicit user instruction.

### Progress
- [x] Renamed `bobp mkf` subcommand to `bobp make` (`bobp/cli.py`, `bobp/tools/mkf.py` ->
      `bobp/tools/make.py`); dropped the now-unused `MKF_ACTIVE` env var
- [x] Removed `_install_makefile()` and its call sites from `bobp/tools/_bob_manage.py`
      (`install()`/`update()` no longer touch a target project's Makefile at all)
- [x] Deleted `bobp/templates/Makefile` — nothing left to install
- [x] Fixed `tests/test_bob_manage.py` (removed the MKF_ACTIVE-in-installed-Makefile test,
      added a test asserting install() does NOT create one)
- [x] Rewrote `make` + `make-discover` skills (live + template `.txt` copies) for the new
      model: no Makefile.prj/Makefile.bob/ifdef split, `bobp make [-v|-vv|-vvv] <target>`
      (flag comes before target — different calling convention than the old `V=` make var)
- [x] Updated judge anti-pattern text (`trace_annotate.py` BUILTIN_RULES + `trace_rules.json`
      + the `MAKE_PIPE_RE`/`MAKE_CHAT_RE` regexes) to reference `bobp make`/`bobp chat`
      instead of bare `make`
- [x] Swept README.md, SHORTHAND_GUIDE.md (root + template), DOCUMENTATION_INDEX.md (root +
      template), render/judge/bob-tools SKILL.md (+ template .txt), and Neo's own SKILL.md
      (+ template .txt) for stale mkf/Makefile.prj/Makefile.bob/MKF_ACTIVE references
- [x] Full test suite green: `26 passed` via the pipx venv's pytest
- [x] Smoke-tested `bobp make test` against bob_protocol's own (untouched) root Makefile —
      capture, tail, exit-code passthrough, and CHAT.md build-status replacement all work
      correctly end-to-end

### Blockers
None

### Oracle Consultations
None — this was a direct user-directed refactor with the design confirmed by the user
mid-task (see Recent Decisions), not something needing historical lookup.

## Next Steps
### Immediate Next Action
Nothing pending from me. Changes are complete and tests pass but are NOT committed — user
has not asked for a commit yet. If asked to commit: `git add` the files in `git status --short`
(all intentional; nothing to exclude) and write a commit message covering both the
`bobp make` rename and the Makefile-ownership handback.

### Waiting On
User review/commit decision. Optionally worth a handoff to Trin (`*qa review`) given the
breadth of the change (CLI rename + doc sweep across ~28 files), though the user only asked
for implementation, not a QA pass — don't assume that's wanted without asking.

### Planned Work
- [ ] None currently queued. Two known-stale, out-of-scope items noted above under Important
      Notes (render skill's make-vs-bobp-make judgment calls; judge skill's
      agents/tools-vs-bobp packaging staleness) if anyone wants to pick them up later.

---
*Last updated: 2026-08-06 17:50*
