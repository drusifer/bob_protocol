# Agent State

## Context
### Recent Decisions
- User decided: persona folders are `agents/<name>/`, not `agents/<name>.docs/`. Applies to this
  repo's `agents/` tree and to the packaged templates, so new installs get the new layout.
- User decided: every tool and doc refers only to the new layout, with one exception —
  `bobp setup-agent-links` must convert older `.docs`-style projects to it. I first misread
  "no back compat" as "remove the conversion too" and pushed that in `bd660c3`; the user
  corrected it and the conversion is restored (`setup_agent_links.migrate_legacy_layout()`,
  the only code that knows the old layout). `bobp update` calls it before refreshing files.
- User asked for `setup-agent-links` to handle `.claude/skills` being a whole-directory symlink
  into `agents/`: it now replaces that link with a real directory before linking.

### Key Findings
- A persona is any folder directly under `agents/` holding a `SKILL.md`
  (`_common.find_persona_dirs()`); `skills/`, `templates/`, `chat_archive/` have none at that
  level, so they are not picked up. Template personas are found by `*/SKILL.md.txt`.
- `tests/test_bob_manage.py::test_install_via_the_real_cli` runs the real `setup_agent_links`.
  Before this session it wrote to the developer's real `~/.codex` — one run repointed the
  skill links and the Codex `via` MCP server at a deleted temp dir. It now sets a throwaway
  `CODEX_HOME`. Repaired by re-running `bobp setup-agent-links` here.
- In this repo `.claude/skills` used to be a symlink to `agents/skills`; it is now a real
  directory with 22 links (9 personas, 13 shared skills).

### Important Notes
- An older `.docs`-style project is converted by `bobp setup-agent-links` or `bobp update`:
  folders renamed, path references in agent docs rewritten. `pull`, `clean`, `diff` do not
  convert — run setup first in such a project.
- `CHAT.md`, `CHAT.diagram.md` and `chat_archive/` deliberately keep the old `.docs` paths as
  history.
- Still open from the 2026-08-06 make cleanup: `agents/skills/render/SKILL.md` has generic
  `make X` mentions that may want `bobp make X`; `agents/skills/judge/SKILL.md`'s
  `make judge-trace` / `trace_annotate.py` invocation model is stale. Neither was touched.

## Current Task
**Status:** Conversion restored and tested (55 passed, 7 skipped) — committed and pushed to `main` (follow-up to `bd660c3`)
**Assigned to:** Neo
**Started:** 2026-10-12
**Commit:** `bd660c3` on `main` (pushed to `origin/main`, was `85d7953`)

### Task Description
Move persona folders from `agents/<name>.docs/` to `agents/<name>/` across the tools, this
repo and the packaged templates, with the tools supporting only the new layout.

### Progress
- [x] `git mv` of all nine persona folders in `agents/` and `bobp/templates/agents/`
- [x] Path references updated in agent docs, skills, templates and root `STARTUP.md`
- [x] `setup_agent_links`, `_bob_manage` (install/update/pull/clean/diff) and `trace_annotate`
      resolve personas via `find_persona_dirs()`; no legacy handling
- [x] `setup-agent-links` replaces a `.claude/skills` directory link into `agents/`
- [x] Integration test isolated with a throwaway `CODEX_HOME`
- [x] Stale `setup_agent_links.py` invocations in SKILL files replaced with
      `bobp setup-agent-links`; `agents/tools/` subtree dropped from the template README
- [x] Tests green: 52 passed, 7 skipped (`bobp make test`)
- [x] Committed (`bd660c3`) and pushed to `origin/main`

### Blockers
None

### Oracle Consultations
None — direct user-directed refactor.

## Next Steps
### Immediate Next Action
None. Next session should read `agents/CHAT.md` for whatever comes in fresh.

### Waiting On
- User: whether to delete the `persona-folder-layout` branch (local and `origin`); it points
  at the same commit as `main`.
- Codex skill links on this machine currently point at bob_protocol; re-run
  `bobp setup-agent-links` in whichever project should own them.

### Planned Work
- [ ] None queued.

---
*Last updated: 2026-10-12 20:44*
